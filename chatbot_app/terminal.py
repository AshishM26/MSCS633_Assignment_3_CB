"""Slash-command handling separated from terminal input and output."""
from dataclasses import dataclass

from django.conf import settings

from chatbot_app.bot_service import BotService

HELP_TEXT = (
    "/help            Show commands\n"
    "/status          Show bot, learning mode, and storage\n"
    "/learning on     Enable conversation learning\n"
    "/learning off    Disable conversation learning\n"
    "/clear           Clear the display only\n"
    "/quit or /exit   End the session"
)


@dataclass(frozen=True)
class CommandResult:
    """Tell the terminal what to display and whether to clear or exit."""

    text: str = ""
    clear: bool = False
    exit: bool = False


def handle_command(message: str, service: BotService) -> CommandResult:
    """Interpret a slash command without manipulating terminal or database."""
    command = " ".join(message.lower().split())
    if command == "/help":
        return CommandResult(HELP_TEXT)
    if command == "/status":
        mode = "ON" if service.learning_enabled else "OFF"
        return CommandResult(
            f"{settings.BOT_NAME} | Learning mode: {mode}\n"
            "Storage: Django ORM / ChatterBot / SQLite"
        )
    if command in {"/learning on", "/learning off"}:
        enabled = command.endswith(" on")
        service.set_learning(enabled)
        return CommandResult(
            f"Continuous learning is now {'ON' if enabled else 'OFF'}."
        )
    if command == "/clear":
        return CommandResult(clear=True)
    if command in {"/quit", "/exit"}:
        return CommandResult("Goodbye!", exit=True)
    return CommandResult("Unknown command. Type /help to view commands.")
