import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Message
from asgiref.sync import sync_to_async
import jwt
from django.conf import settings
from urllib.parse import parse_qs
from jwt import decode as jwt_decode


class ChatConsumer(AsyncJsonWebsocketConsumer):
    @sync_to_async
    def save_message(self, conversation_id, sender_id, content):
        return Message.objects.create(
            conversation_id=conversation_id, sender_id=sender_id, content=content
        )

    async def connect(self):
        """
        Handle WebSocket connection with JWT authentication.
        """
        # Extract JWT from query params
        query_string = self.scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if not token:
            print("WebSocket connection attempt without token")
            await self.accept()  # Accept first to send error message
            await self.send_json({"type": "error", "message": "Missing token"})
            await self.close(code=4001)
            return

        # Verify JWT and get user
        try:
            # Decode JWT token using Django SECRET_KEY
            # simplejwt uses HS256 by default with Django SECRET_KEY
            payload = jwt_decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_exp": True},
            )
            user_id = payload.get("user_id")
            self.user_id = user_id

            if not user_id:
                print("JWT token missing user_id")
                await self.accept()
                await self.send_json(
                    {"type": "error", "message": "Invalid token payload"}
                )
                await self.close(code=4002)
                return

            self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
            self.room_group_name = f"chat_{self.conversation_id}"

            # Join group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()

            print(
                f"User {self.user_id} connected to conversation {self.conversation_id}"
            )

        except jwt.ExpiredSignatureError:
            print("JWT token expired")
            await self.accept()
            await self.send_json({"type": "error", "message": "Token expired"})
            await self.close(code=4005)
            return
        except jwt.InvalidTokenError as e:
            print(f"Invalid JWT token: {e}")
            await self.accept()
            await self.send_json({"type": "error", "message": "Invalid token"})
            await self.close(code=4006)
            return
        except Exception as e:
            print(f"JWT decode error: {type(e).__name__}: {e}")
            await self.accept()
            await self.send_json(
                {"type": "error", "message": f"JWT verification failed: {str(e)}"}
            )
            await self.close(code=4004)
            return

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Triggered when the client sends message through WebSocket.
        """
        data = json.loads(text_data)
        message = data.get("message")
        sender_id = self.user_id

        # Save message to DB
        msg = await self.save_message(self.conversation_id, sender_id, message)

        # Broadcast message to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",  # function below
                "content": msg.content,
                "created_at": str(msg.created_at),
                "sender": self.user_id,
            },
        )

    async def chat_message(self, event):
        """
        Called by group_send.
        """
        await self.send(text_data=json.dumps(event))
