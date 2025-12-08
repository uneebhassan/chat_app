from django.urls import path
from .views import ConversationsAPIView, MessagesAPIView, UserAPIView

urlpatterns = [
    path("conversations/", ConversationsAPIView.as_view(), name="conversations"),
    path("messages/", MessagesAPIView.as_view(), name="messages"),
    path("new_users/", UserAPIView.as_view(), name="messages"),
]
