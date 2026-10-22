"""Exercise real ChatterBot matching and persistence through Django ORM."""
from chatterbot.trainers import ListTrainer
from django.conf import settings
from django.test import TestCase

from chatbot_app.bot_service import BotService


class BotServiceTests(TestCase):
    """Use tiny known conversations for deterministic integration tests."""

    @classmethod
    def setUpTestData(cls):
        cls.service = BotService(learning_enabled=False)
        trainer = ListTrainer(cls.service.bot, show_training_progress=False)
        trainer.train(["What is CI?", "CI runs automated builds and tests."])

    def setUp(self):
        self.service = BotService(learning_enabled=False)

    def test_initializes_django_storage(self):
        self.assertEqual(self.service.bot.storage.database, "default")
        self.assertEqual(self.service.bot.name, settings.BOT_NAME)

    def test_returns_full_trained_text(self):
        reply = self.service.get_response("What is CI?")
        self.assertEqual(reply.text, "CI runs automated builds and tests.")
        self.assertEqual(reply.confidence, 1.0)

    def test_read_only_does_not_save(self):
        before = self.service.bot.storage.count()
        self.service.get_response("What is CI?")
        self.assertEqual(self.service.bot.storage.count(), before)

    def test_learning_toggle_changes_actual_persistence(self):
        before = self.service.bot.storage.count()
        self.service.set_learning(True)
        self.assertTrue(self.service.learning_enabled)
        self.service.get_response("What is CI?")
        after = self.service.bot.storage.count()
        self.assertGreater(after, before)
        self.service.set_learning(False)
        self.assertFalse(self.service.learning_enabled)
        self.service.get_response("What is CI?")
        self.assertEqual(self.service.bot.storage.count(), after)

    def test_unknown_input_falls_back_without_learning_bad_answer(self):
        self.service.set_learning(True)
        before = self.service.bot.storage.count()
        reply = self.service.get_response(
            "purple intergalactic marshmallow parade"
        )
        self.assertEqual(reply.text, settings.BOT_FALLBACK)
        self.assertLess(reply.confidence, settings.BOT_MIN_CONFIDENCE)
        self.assertEqual(self.service.bot.storage.count(), before)

    def test_invalid_messages(self):
        for message in ["", "  ", None, 3, "a" * 501]:
            with self.subTest(message=message), self.assertRaises(ValueError):
                self.service.get_response(message)

    def test_separate_instances_isolate_learning_mode(self):
        terminal = BotService()
        self.assertTrue(terminal.learning_enabled)
        self.assertFalse(self.service.learning_enabled)

    def test_persistence_available_to_new_instance(self):
        second = BotService(learning_enabled=False)
        self.assertEqual(second.get_response("What is CI?").confidence, 1.0)
