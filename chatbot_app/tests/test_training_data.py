"""Check corpus structure, coverage, and actual learned responses."""
from io import StringIO

import yaml
from chatterbot.trainers import ChatterBotCorpusTrainer
from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from chatbot_app.bot_service import BotService


class CorpusStructureTests(SimpleTestCase):
    """Read the actual distribution resource."""

    def test_valid_custom_corpus_and_minimum_pairs(self):
        path = settings.BASE_DIR / "data/cloud_devops.yml"
        self.assertTrue(path.is_file())
        corpus = yaml.safe_load(path.read_text())
        self.assertIn("cloud_devops", corpus["categories"])
        pairs = [item for item in corpus["conversations"] if len(item) == 2]
        self.assertGreaterEqual(len(pairs), 30)
        for conversation in corpus["conversations"]:
            self.assertGreaterEqual(len(conversation), 2)
            for text in conversation:
                self.assertIsInstance(text, str)
                self.assertTrue(text.strip())


class CorpusRuntimeTests(TestCase):
    """Verify full training and repeat runs only in the test database."""

    def test_custom_questions_return_their_answers(self):
        service = BotService(learning_enabled=False)
        path = settings.BASE_DIR / "data/cloud_devops.yml"
        trainer = ChatterBotCorpusTrainer(
            service.bot, show_training_progress=False
        )
        trainer.train(str(path))
        corpus = yaml.safe_load(path.read_text())
        for conversation in corpus["conversations"]:
            with self.subTest(question=conversation[0]):
                self.assertEqual(
                    service.get_response(conversation[0]).text, conversation[1]
                )

    def test_unrelated_topics_with_similar_question_wording_fall_back(self):
        call_command("train_bot", stdout=StringIO())
        service = BotService(learning_enabled=False)
        for question in ["What is pizza?", "What is a banana?",
                         "What is the capital of France?",
                         "What is quantum entanglement?"]:
            with self.subTest(question=question):
                self.assertEqual(
                    service.get_response(question).text, settings.BOT_FALLBACK
                )

    def test_retraining_preserves_existing_knowledge(self):
        service = BotService(learning_enabled=False)
        call_command("train_bot", stdout=StringIO())
        before = service.bot.storage.count()
        call_command("train_bot", stdout=StringIO())
        # DjangoStorageAdapter inserts rows on repeat training; no deletion.
        self.assertEqual(service.bot.storage.count(), before * 2)
        reply = service.get_response("What is Terraform?")
        self.assertIn("Terraform", reply.text)
