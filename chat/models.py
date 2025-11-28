from common.models import UUIDTimeStampedModelMixin
from django.db import models
from common.constants import USER_MODEL
from common.choices import CONVERSATION_TYPES


class Conversation(UUIDTimeStampedModelMixin):
    """
    Represents a chat conversation, which can be either a direct (one-to-one)
    chat or a group chat. Each conversation may optionally have a title, which
    is typically used for group chats. The model inherits timestamp fields and
    a UUID primary key from `UUIDTimeStampedModelMixin`.
    """

    type = models.CharField(max_length=10, choices=CONVERSATION_TYPES)
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional name for the conversation, mainly used for group chats.",
    )

    def __str__(self):
        return self.title or f"{self.type} conversation {self.id}"


class ConversationMember(UUIDTimeStampedModelMixin):
    """
    Defines a participant in a conversation. Each entry links a user to a
    conversation. Users within the same conversation must be unique, enforced
    by the `unique_together` constraint. Useful for both direct and group chats.
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="members",
        help_text="The conversation this user is participating in.",
    )
    user = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user who is part of the conversation.",
    )

    class Meta:
        unique_together = ("conversation", "user")
        verbose_name = "Conversation Member"
        verbose_name_plural = "Conversation Members"

    def __str__(self):
        return f"{self.user.username} in {self.conversation.id}"


class Message(UUIDTimeStampedModelMixin):
    """
    Represents a text message sent within a conversation. Each message belongs
    to a conversation and has a sender (User). This model stores only plain text
    messages, without attachments or additional metadata.
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="The conversation in which this message was sent.",
    )
    sender = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user who sent the message.",
    )
    content = models.TextField(help_text="The text content of the message.")

    def __str__(self):
        return f"Message {self.id} from {self.sender.username}"
