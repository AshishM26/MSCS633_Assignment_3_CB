"""Train selected English corpora and custom CloudOps conversations."""
from chatterbot.trainers import ChatterBotCorpusTrainer
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from chatbot_app.bot_service import BotService


class Command(BaseCommand):
    """Train without deleting existing conversations."""

    help = "Train English greetings, conversations, and custom CloudOps Q&A."

    def handle(self, *args, **options) -> None:
        """Commit a complete training run or roll back on failure."""
        corpora = [
            (
                "English greetings corpus",
                "chatterbot.corpus.english.greetings",
            ),
            (
                "English conversations corpus",
                "chatterbot.corpus.english.conversations",
            ),
            (
                "Cloud/DevOps custom corpus",
                str(settings.BASE_DIR / "data/cloud_devops.yml"),
            ),
        ]
        self.stdout.write(f"Training {settings.BOT_NAME}...")
        try:
            service = BotService(learning_enabled=False)
            trainer = ChatterBotCorpusTrainer(
                service.bot, show_training_progress=False
            )
            with transaction.atomic():
                for index, (label, corpus) in enumerate(corpora, start=1):
                    self.stdout.write(f"[{index}/3] {label}")
                    trainer.train(corpus)
        except Exception as exc:
            raise CommandError(
                f"Training failed; changes rolled back: {exc}"
            ) from exc
        self.stdout.write(self.style.SUCCESS("Training complete."))
