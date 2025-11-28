from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class Index(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {"message": "Hello from Class Based API"}
        return Response(data)
