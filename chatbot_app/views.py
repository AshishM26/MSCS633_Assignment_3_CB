"""Small, CSRF-protected JSON demonstration endpoints."""
import json
import logging

from django.conf import settings
from django.core.exceptions import RequestDataTooBig
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from chatbot_app.bot_service import BotService

logger = logging.getLogger(__name__)


@require_GET
@ensure_csrf_cookie
def health(request: HttpRequest) -> JsonResponse:
    """Report application liveness and issue a CSRF cookie for the demo."""
    return JsonResponse({
        "status": "ok", "bot": settings.BOT_NAME,
        "framework": "Django", "engine": "ChatterBot",
    })


@require_POST
def chat(request: HttpRequest) -> JsonResponse:
    """Answer one message with learning disabled for every API request."""
    if request.content_type != "application/json":
        return JsonResponse({"error": "Use application/json."}, status=415)
    try:
        data = json.loads(request.body)
    except RequestDataTooBig:
        return JsonResponse(
            {"error": "Request body is too large."}, status=413
        )
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Malformed JSON."}, status=400)
    message = data.get("message") if isinstance(data, dict) else None
    if not isinstance(message, str) or not message.strip():
        return JsonResponse(
            {"error": "Provide a non-empty message string."}, status=400
        )
    if len(message.strip()) > settings.BOT_MAX_MESSAGE_LENGTH:
        return JsonResponse(
            {"error": "Message exceeds 500 characters."}, status=400
        )
    try:
        service = BotService(learning_enabled=False)
        reply = service.get_response(message)
    except Exception:
        logger.exception("Chat API response failed")
        return JsonResponse(
            {"error": "Chatbot is temporarily unavailable."}, status=503
        )
    return JsonResponse({
        "message": message.strip(), "response": reply.text,
        "confidence": reply.confidence,
        "learning_enabled": reply.learning_enabled,
    })


def csrf_failure(request: HttpRequest, reason: str = "") -> JsonResponse:
    """Return a JSON error without exposing internal CSRF diagnostics."""
    return JsonResponse(
        {"error": "A valid CSRF cookie and token are required."}, status=403
    )
