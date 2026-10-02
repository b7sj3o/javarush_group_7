from rest_framework import serializers


class ContactSerializer(serializers.Serializer):
    """Форма зворотного зв'язку. Без моделі — звернення нікуди не зберігаємо."""

    SUBJECT_CHOICES = [
        ("product", "Питання про товар"),
        ("order", "Питання про замовлення"),
        ("delivery", "Доставка й оплата"),
        ("return", "Повернення / обмін"),
        ("other", "Інше"),
    ]

    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    subject = serializers.ChoiceField(choices=SUBJECT_CHOICES)
    order_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    message = serializers.CharField()
    consent = serializers.BooleanField()

    def validate_message(self, value):
        message = value.strip()
        if len(message) < 10:
            raise serializers.ValidationError(
                "Повідомлення надто коротке — опишіть детальніше (мін. 10 символів)."
            )
        return message

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError("Потрібна згода на обробку персональних даних.")
        return value

    def validate(self, attrs):
        if attrs["subject"] in ("order", "return") and not attrs.get("order_number"):
            raise serializers.ValidationError(
                {"order_number": "Для цієї теми вкажіть номер замовлення."}
            )
        return attrs
