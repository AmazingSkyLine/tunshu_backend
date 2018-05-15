from . import consumers
from django.urls import path


websocket_urlpatterns = [
    path('ws/messages/main/', consumers.MainConsumer),
]
