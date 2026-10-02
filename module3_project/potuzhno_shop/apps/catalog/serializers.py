from rest_framework import serializers

from .models import Brand, Category, Product, Size, unique_slug


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "created_at")
        read_only_fields = ("created_at",)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug")


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ("id", "name")


class ProductReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    sizes = serializers.SlugRelatedField(  # [1, 3, 6] -> ["S", "XL", "L"]
        many=True, slug_field="name", read_only=True
    )
    avg_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    # Анотація з ProductViewSet.get_queryset(); для об'єктів без анотації — False
    is_favourite = serializers.BooleanField(read_only=True, default=False)
    # Точний stock бачить лише staff (див. to_representation),
    # але «є/немає в наявності» показуємо всім
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "description", "price",
            "category", "brand", "audience", "sizes",
            "stock", "sku", "is_active", "is_featured",
            "avg_rating", "reviews_count", "is_favourite", "in_stock",
            "created_at", "updated_at",
        )

    def get_in_stock(self, obj) -> bool:
        return obj.stock > 0

    def get_avg_rating(self, obj) -> float | None:
        return getattr(obj, "avg_rating", 0)

    def get_reviews_count(self, obj) -> int:
        return getattr(obj, "reviews_count", 0)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        if not (request and request.user.is_staff):
            representation.pop("sku", None)
            representation.pop("stock", None)

        return representation


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id", "name", "description", "price",
            "category", "brand", "audience", "sizes",
            "stock", "sku", "is_active", "is_featured",
            "created_at", "updated_at",
        )

    def validate_price(self, price):
        if price <= 0:
            raise serializers.ValidationError("Ціна має бути більшою за 0.")
        return price

    def validate_stock(self, stock):
        if stock < 0:
            raise serializers.ValidationError("К-сть товару не може бути від'ємною.")
        return stock

    def validate(self, attrs):
        is_featured = attrs.get("is_featured", getattr(self.instance, "is_featured", False))
        stock = attrs.get("stock", getattr(self.instance, "stock", 0))

        if is_featured and stock == 0:
            raise serializers.ValidationError({
                "is_featured": "Не можна рекомендувати товар, якого немає в наявності.",
            })

        return attrs

    def create(self, validated_data):
        sizes = validated_data.pop("sizes") if "sizes" in validated_data else None
        validated_data["slug"] = unique_slug(validated_data["name"])

        product = Product.objects.create(**validated_data)
        if sizes:
            product.sizes.set(sizes)  # Обов'язково при M2M

        return product

    def update(self, instance, validated_data):
        if "name" in validated_data and validated_data["name"] != instance.name:
            validated_data["slug"] = unique_slug(validated_data["name"], instance=instance)
        return super().update(instance, validated_data)


class ProductMiniSerializer(serializers.ModelSerializer):
    """Мінімум даних про товар (напр. усередині відгуку) — щоб фронтенд міг дати посилання."""

    class Meta:
        model = Product
        fields = ("id", "name", "slug")
