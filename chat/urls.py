from django.urls import path
from .views import ConversationsAPIView, MessagesAPIView

urlpatterns = [
    path("conversations/", ConversationsAPIView.as_view(), name="conversations"),
    path("messages/", MessagesAPIView.as_view(), name="messages"),
]
