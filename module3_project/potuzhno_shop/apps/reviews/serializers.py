from rest_framework import serializers

from apps.catalog.models import Product
from apps.catalog.serializers import ProductMiniSerializer

from .models import Review


class ReviewReadSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    # React-профілю потрібен slug товару для посилання, тому не StringRelatedField
    product = ProductMiniSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "user", "product", "rating", "text", "created_at")


class ReviewWriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Review
        fields = ("id", "user", "product", "rating", "text", "created_at")
        read_only_fields = ("created_at",)

    def validate(self, attrs):
        rating = attrs.get("rating", getattr(self.instance, "rating", 5))
        text = attrs.get("text", getattr(self.instance, "text", "")).strip()

        if rating <= 2 and len(text) < 5:
            raise serializers.ValidationError({
                "text": "Для оцінки 1–2 поясніть, що не сподобалось (мінімум 5 символів).",
            })

        return attrs
