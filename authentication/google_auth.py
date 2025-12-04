# accounts/views.py
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class GoogleAuthView(APIView):
    """
    POST { "id_token": "<google-id-token>" }
    """

    permission_classes = []  # allow any for auth

    def post(self, request, *args, **kwargs):
        token = request.data.get("id_token")
        if not token:
            return Response(
                {"detail": "No ID token provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify the token. Replace CLIENT_ID with your Google OAuth client ID.
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )

            # idinfo contains: 'sub' (google user id), 'email', 'email_verified', 'name', 'picture', etc.
            if not idinfo.get("email_verified"):
                return Response(
                    {"detail": "Email not verified by Google."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            email = idinfo.get("email")
            name = idinfo.get("name", "")
            google_sub = idinfo.get("sub")

            # Find or create a local user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email.split("@")[0],
                    "first_name": name.split(" ")[0] if name else "",
                    "last_name": " ".join(name.split(" ")[1:])
                    if name and len(name.split(" ")) > 1
                    else "",
                },
            )

            # Optionally, save google_sub to user profile to link accounts (create a profile model)
            # e.g., user.profile.google_sub = google_sub; user.profile.save()

            # Create JWT tokens for this user (SimpleJWT)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                    },
                }
            )

        except ValueError as e:
            # Token invalid
            return Response(
                {"detail": "Invalid ID token", "exception": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
