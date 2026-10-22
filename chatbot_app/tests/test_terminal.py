"""Exercise command parsing and normal terminal exit/error paths."""
from io import StringIO
from unittest.mock import patch

from chatterbot.trainers import ListTrainer
from django.core.management import call_command
from django.test import TestCase

from chatbot_app.bot_service import BotService
from chatbot_app.terminal import handle_command


class TerminalTests(TestCase):
    """Test command I/O without requiring a human terminal."""

    @classmethod
    def setUpTestData(cls):
        cls.service = BotService(learning_enabled=False)
        trainer = ListTrainer(cls.service.bot, show_training_progress=False)
        trainer.train(["Hi", "Hello!"])

    def test_help_status_and_learning(self):
        service = BotService()
        self.assertIn("/clear", handle_command("/help", service).text)
        self.assertIn("Django", handle_command("/status", service).text)
        handle_command("/learning off", service)
        self.assertIn("OFF", handle_command("/status", service).text)
        handle_command("/learning on", service)
        self.assertTrue(service.learning_enabled)

    def test_clear_never_erases_knowledge(self):
        before = self.service.bot.storage.count()
        self.assertTrue(handle_command("/clear", self.service).clear)
        self.assertEqual(self.service.bot.storage.count(), before)

    def test_quit_and_exit(self):
        for command in ["/quit", "/exit"]:
            self.assertTrue(handle_command(command, self.service).exit)

    def test_unknown_command(self):
        result = handle_command("/learning maybe", self.service)
        self.assertIn("Unknown", result.text)

    def test_empty_input_and_clean_exit(self):
        output = StringIO()
        with patch("builtins.input", side_effect=["", "Hi", "/exit"]):
            call_command("chat", stdout=output)
        self.assertIn("Bot: Hello!", output.getvalue())
        self.assertIn("Goodbye!", output.getvalue())

    def test_eof_and_ctrl_c(self):
        for interrupt in [EOFError, KeyboardInterrupt]:
            output = StringIO()
            with patch("builtins.input", side_effect=interrupt):
                call_command("chat", stdout=output)
            self.assertIn("Goodbye!", output.getvalue())

    def test_runtime_error_allows_exit(self):
        output, errors = StringIO(), StringIO()
        with patch("builtins.input", side_effect=["Hi", "/exit"]):
            with patch.object(
                BotService, "get_response", side_effect=RuntimeError("test")
            ):
                with self.assertLogs(
                    "chatbot_app.management.commands.chat", level="ERROR"
                ):
                    call_command("chat", stdout=output, stderr=errors)
        self.assertIn("Something went wrong", errors.getvalue())
        self.assertIn("Goodbye!", output.getvalue())
