import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ContactSerializer

logger = logging.getLogger("contact")


class ContactView(APIView):
    """
    POST /api/v1/contact/ — звернення з форми «Контакти».
    Нікуди не зберігає — лише пише в лог (див. LOGGING у settings).
    """

    permission_classes = (AllowAny,)
    serializer_class = ContactSerializer  # також потрібен drf-spectacular для Swagger

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        logger.info(
            "CONTACT: name=%s email=%s subject=%s order=%s message=%s",
            data["name"], data["email"], data["subject"],
            data.get("order_number") or "-", data["message"],
        )

        return Response(
            {"detail": f"Дякуємо, {data['name']}! Ми відповімо на {data['email']}."},
            status=status.HTTP_200_OK,
        )
