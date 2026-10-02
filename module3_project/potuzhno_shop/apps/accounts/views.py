from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegisterSerializer, UserSerializer


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """POST /token/ — логін: видає пару access/refresh. Обмежено 5 спроб/хв."""

    throttle_scope = "login"


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_scope = "login"


class RegisterView(generics.CreateAPIView):
    """
    POST /auth/register/ — реєстрація.
    "Залогінити" в API = одразу видати пару JWT-токенів разом із даними користувача.
    """

    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    throttle_scope = "register"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": {"id": user.id, "username": user.username},
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(generics.RetrieveUpdateAPIView):
    """
    GET /users/me/ — дані поточного користувача.
    PATCH — оновлення email та phone/address з Profile.
    """

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user
