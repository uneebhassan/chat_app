from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message, ConversationMember
from authentication.models import CustomUser
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer
from .api_info import create_conversation_request_body
from drf_yasg.utils import swagger_auto_schema


class ConversationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Conversation.objects.filter(
            type="direct", members__user=request.user
        ).distinct()
        data = ConversationSerializer(
            queryset, many=True, context={"user": request.user}
        ).data
        return Response(data)

    @swagger_auto_schema(
        request_body=create_conversation_request_body,
        responses={201: ConversationSerializer},
    )
    def post(self, request):
        # Create the conversation
        user_id = request.data.get("user_id")

        try:
            selected_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=400)

        conversation = Conversation.objects.create(type="direct", title="")

        # Add the requesting user as a member
        ConversationMember.objects.create(conversation=conversation, user=request.user)
        ConversationMember.objects.create(conversation=conversation, user=selected_user)

        # Serialize result
        data = ConversationSerializer(conversation, context={"user": request.user}).data
        return Response(data)


class MessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversation_id = request.GET.get("conversation_id")
        queryset = Message.objects.filter(conversation_id=conversation_id)
        data = MessageSerializer(queryset, many=True).data
        return Response(data)


class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_user = request.user

        # Get IDs of users who share a conversation with the current user
        user_conversations = Conversation.objects.filter(
            members__user=current_user
        ).values_list("id", flat=True)

        conversation_users = Conversation.objects.filter(
            id__in=user_conversations
        ).values_list("members__user__id", flat=True)

        # Exclude the current user and users already in conversations with them
        available_users = CustomUser.objects.exclude(id__in=conversation_users).exclude(
            id=current_user.id
        )

        data = UserSerializer(available_users, many=True).data
        return Response(data)
