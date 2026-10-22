"""Local educational settings; terminal and API share Django's SQLite store."""
import os
import secrets
from pathlib import Path

from chatterbot.tagging import LowercaseTagger

BASE_DIR = Path(__file__).resolve().parent.parent
# No persistent secret is needed for this sessionless local demonstration.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or secrets.token_urlsafe(50)
DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "chatbot_app",
    "chatterbot.ext.django_chatterbot",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]
ROOT_URLCONF = "smartchat.urls"
WSGI_APPLICATION = "smartchat.wsgi.application"
ASGI_APPLICATION = "smartchat.asgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Chicago"
USE_TZ = True
CSRF_FAILURE_VIEW = "chatbot_app.views.csrf_failure"
DATA_UPLOAD_MAX_MEMORY_SIZE = 8192

BOT_NAME = "CloudOps Assistant"
# Shared wording such as "What is" can give unrelated topics a score of 0.85.
BOT_MIN_CONFIDENCE = 0.90
BOT_MAX_MESSAGE_LENGTH = 500
BOT_FALLBACK = (
    "I'm not confident about that yet. Try rephrasing the question "
    "or teach me through another conversation."
)
CHATTERBOT = {
    "name": BOT_NAME,
    "storage_adapter": "chatterbot.storage.DjangoStorageAdapter",
    # Built-in lowercase indexing avoids a separate downloaded language model.
    "tagger": LowercaseTagger,
    "logic_adapters": [{
        "import_path": "chatterbot.logic.BestMatch",
        "default_response": BOT_FALLBACK,
        "maximum_similarity_threshold": 1.0,
    }],
    "read_only": False,
}
