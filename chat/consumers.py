import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        # Join group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Triggered when the client sends message through WebSocket.
        """
        data = json.loads(text_data)
        message = data.get("message")
        sender_id = self.scope["user"].id

        # Save message to DB
        msg = Message.objects.create(
            conversation_id=self.conversation_id, sender_id=sender_id, content=message
        )

        # Broadcast message to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",  # function below
                "message": msg.content,
                "sender": msg.sender.username,
                "timestamp": str(msg.created_at),
            },
        )

    async def chat_message(self, event):
        """
        Called by group_send.
        """
        await self.send(text_data=json.dumps(event))
