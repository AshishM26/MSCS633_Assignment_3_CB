"""Root routes for the small Django demonstration API."""
from django.urls import include, path

urlpatterns = [path("api/", include("chatbot_app.urls"))]
