"""API endpoint routes."""
from django.urls import path

from chatbot_app import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("chat/", views.chat, name="chat"),
]
