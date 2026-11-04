from django.urls import path
from . import consumers
from typing import Any, cast

websocket_urlpatterns = [
    path("ws/signaling/", cast(Any, consumers.SignalingConsumer.as_asgi())),
]