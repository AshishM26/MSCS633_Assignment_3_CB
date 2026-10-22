"""Validate HTTP input, CSRF, and read-only database behavior."""
from unittest.mock import patch

from chatterbot.trainers import ListTrainer
from django.conf import settings
from django.test import Client, TestCase

from chatbot_app.bot_service import BotService


class ApiTests(TestCase):
    """Exercise real views and ChatterBot with a tiny training fixture."""

    @classmethod
    def setUpTestData(cls):
        cls.service = BotService(learning_enabled=False)
        ListTrainer(cls.service.bot, show_training_progress=False).train(
            ["What is CI?", "CI runs automated builds and tests."]
        )

    def post(self, data):
        """Send JSON using Django's test client."""
        return self.client.post(
            "/api/chat/", data, content_type="application/json"
        )

    def test_health(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "ok", "bot": settings.BOT_NAME,
            "framework": "Django", "engine": "ChatterBot",
        })

    def test_valid_response_and_read_only(self):
        before = self.service.bot.storage.count()
        response = self.post({
            "message": "What is CI?", "learning_enabled": True,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["response"], "CI runs automated builds and tests."
        )
        self.assertFalse(response.json()["learning_enabled"])
        self.assertEqual(self.service.bot.storage.count(), before)

    def test_empty_or_invalid_message(self):
        for data in [{}, {"message": " "}, {"message": None},
                     {"message": 12}, [], {"message": "x" * 501}]:
            with self.subTest(data=data):
                self.assertEqual(self.post(data).status_code, 400)

    def test_malformed_json(self):
        self.assertEqual(self.post('{"message":').status_code, 400)

    def test_invalid_encoding(self):
        self.assertEqual(self.post(b"\xff").status_code, 400)

    def test_content_type(self):
        response = self.client.post("/api/chat/", {"message": "Hi"})
        self.assertEqual(response.status_code, 415)

    def test_method_validation(self):
        self.assertEqual(self.client.get("/api/chat/").status_code, 405)
        self.assertEqual(self.client.post("/api/health/").status_code, 405)

    def test_oversized_body(self):
        self.assertEqual(self.post({"message": "x" * 9000}).status_code, 413)

    def test_csrf_is_required_and_valid_token_works(self):
        client = Client(enforce_csrf_checks=True)
        data = {"message": "What is CI?"}
        self.assertEqual(client.post(
            "/api/chat/", data, content_type="application/json"
        ).status_code, 403)
        client.get("/api/health/")
        response = client.post(
            "/api/chat/", data, content_type="application/json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )
        self.assertEqual(response.status_code, 200)

    def test_runtime_failure_returns_503(self):
        with patch(
            "chatbot_app.views.BotService", side_effect=RuntimeError("test")
        ):
            with self.assertLogs("chatbot_app.views", level="ERROR"):
                response = self.post({"message": "Hello"})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("test", response.content.decode())
