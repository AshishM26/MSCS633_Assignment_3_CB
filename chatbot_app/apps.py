"""Django app registration."""
from django.apps import AppConfig


class ChatbotAppConfig(AppConfig):
    """Register the terminal and API application."""

    name = "chatbot_app"
    default_auto_field = "django.db.models.AutoField"
