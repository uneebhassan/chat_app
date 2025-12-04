from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationsAPIView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = Conversation.objects.filter(type="direct")
        data = ConversationSerializer(
            queryset, many=True, context={"user": request.user}
        ).data
        return Response(data)


class MessagesAPIView(APIView):
    permission_classes = []

    def get(self, request):
        conversation_id = request.GET.get("conversation_id")
        queryset = Message.objects.filter(conversation_id=conversation_id)
        data = MessageSerializer(queryset, many=True).data
        return Response(data)
