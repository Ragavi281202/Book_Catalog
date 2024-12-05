from django.urls import path
from . import consumers  

websocket_urlpatterns = [
    path('ws/book_notification/', consumers.BookNotificationConsumer.as_asgi()),
]
