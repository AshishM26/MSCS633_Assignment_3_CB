"""Shared ChatterBot construction and response policy, independent of I/O."""
from copy import deepcopy
from dataclasses import dataclass

from chatterbot import ChatBot
from django.conf import settings
from django.db import transaction


@dataclass(frozen=True)
class BotReply:
    """A response with similarity confidence, not a probability of truth."""

    text: str
    confidence: float
    learning_enabled: bool


class BotService:
    """Own one bot per conversation; API requests explicitly use read-only."""

    def __init__(self, *, learning_enabled: bool = True) -> None:
        config = deepcopy(settings.CHATTERBOT)
        # ChatterBot 1.2.15's Django AppConfig overwrites CHATTERBOT['name'].
        # Keep our authoritative name outside the upstream mutable defaults.
        config.pop("name", None)
        config["read_only"] = not learning_enabled
        self.bot = ChatBot(settings.BOT_NAME, **config)

    @property
    def learning_enabled(self) -> bool:
        """Report ChatterBot's current persistence behavior."""
        return not self.bot.read_only

    def set_learning(self, enabled: bool) -> None:
        """Toggle persistence while preserving stored knowledge."""
        self.bot.read_only = not enabled

    def get_response(self, message: str) -> BotReply:
        """Validate input and replace weak matches with a graceful fallback."""
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Message must be a non-empty string.")
        message = message.strip()
        if len(message) > settings.BOT_MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"Message must be at most {settings.BOT_MAX_MESSAGE_LENGTH} "
                "characters."
            )
        with transaction.atomic():
            response = self.bot.get_response(message)
            confidence = float(response.confidence)
            text = response.text
            if confidence < settings.BOT_MIN_CONFIDENCE:
                text = settings.BOT_FALLBACK
                # Do not retain a weak answer hidden by the fallback.
                transaction.set_rollback(True)
        return BotReply(text, confidence, self.learning_enabled)
