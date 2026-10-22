"""Interactive terminal client launched through Django."""
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from chatbot_app.bot_service import BotService
from chatbot_app.terminal import handle_command

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run the required terminal conversation loop."""

    help = "Chat with CloudOps Assistant. Use /help for commands."

    def handle(self, *args, **options) -> None:
        """Handle normal input, control commands, EOF, and interruptions."""
        try:
            service = BotService()
            if service.bot.storage.count() == 0:
                raise CommandError(
                    "No training data. Run: python manage.py train_bot"
                )
        except CommandError:
            raise
        except Exception as exc:
            raise CommandError(
                "Cannot initialize chatbot. Check setup and run migrate. "
                f"Details: {exc}"
            ) from exc
        self.stdout.write(
            "========================================\n"
            f" {settings.BOT_NAME}\n"
            " MSCS-633 Hands-On Assignment 3\n"
            "========================================\n"
            "Type /help to view commands.\nLearning mode: ON\n"
        )
        while True:
            try:
                message = input("You: ").strip()
                if not message:
                    continue
                if message.startswith("/"):
                    result = handle_command(message, service)
                    if result.clear:
                        self.stdout.write("\033[2J\033[H", ending="")
                    if result.text:
                        self.stdout.write(f"Bot: {result.text}")
                    if result.exit:
                        return
                else:
                    reply = service.get_response(message)
                    self.stdout.write(f"Bot: {reply.text}\n")
            except (EOFError, KeyboardInterrupt):
                self.stdout.write("\nBot: Goodbye!")
                return
            except ValueError as exc:
                self.stdout.write(f"Bot: {exc}")
            except Exception:
                # Keep the interactive session alive, but preserve diagnostics.
                logger.exception("Unable to process the terminal message")
                self.stderr.write(
                    "Bot: Something went wrong. See the diagnostic above; "
                    "try again or use /exit."
                )
