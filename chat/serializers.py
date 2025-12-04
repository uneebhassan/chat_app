from rest_framework import serializers
from .models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = "__all__"  # or explicitly: ['id', 'type', 'members', 'title']

    def get_title(self, obj):
        user = self.context.get("user")

        if obj.type == "direct":
            # Exclude the current user to get the other participant
            other_user = obj.members.all().exclude(user=user).first() if user else None
            return other_user.user.username if other_user.user else "Unknown"
        elif obj.type == "group":
            return obj.title
        return "Conversation"


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
