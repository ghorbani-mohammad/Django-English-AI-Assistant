from django.urls import path

from . import consumer

websocket_urlpatterns = [
    path("chat/<str:uid>/", consumer.ChatConsumer.as_asgi()),
]
