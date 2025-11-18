from rest_framework.views import APIView
from rest_framework.response import Response


class Index(APIView):
    def get(self, request):
        data = {"message": "Hello from Class Based API"}
        return Response(data)
