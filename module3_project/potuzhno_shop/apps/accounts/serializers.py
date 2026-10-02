from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("id", "username", "password", "password2")

    def validate_password(self, value):
        # Проганяє AUTH_PASSWORD_VALIDATORS із settings
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Паролі не збігаються."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        # create_user хешує пароль; звичайний create зберіг би його відкритим текстом
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """GET/PATCH /users/me/ — дані User + поля Profile (phone, address)."""

    phone = serializers.CharField(
        source="profile.phone", max_length=20, allow_blank=True, required=False
    )
    address = serializers.CharField(
        source="profile.address", max_length=255, allow_blank=True, required=False
    )
    groups = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "phone", "address",
            "date_joined", "is_staff", "is_superuser", "groups",
        )
        read_only_fields = ("id", "username", "date_joined", "is_staff", "is_superuser")

    def update(self, instance, validated_data):
        # source="profile.*" складає вкладені поля у validated_data["profile"]
        profile_data = validated_data.pop("profile", {})
        instance = super().update(instance, validated_data)

        if profile_data:
            for field, value in profile_data.items():
                setattr(instance.profile, field, value)
            instance.profile.save()

        return instance
