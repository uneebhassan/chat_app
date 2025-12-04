from django.urls import path
from .views import RegisterView, MyTokenObtainPairView
from .google_auth import GoogleAuthView
from rest_framework_simplejwt.views import TokenRefreshView


app_urls = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

google_auth_urls = [
    path("google/", GoogleAuthView.as_view(), name="google_auth"),
]

urlpatterns = app_urls + google_auth_urls
