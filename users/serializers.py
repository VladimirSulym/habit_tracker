from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "city", "password")
        extra_kwargs = {"password": {"write_only": True}}

    @staticmethod
    def validate_phone(value):
        if value and not value.replace("+", "").isdigit():
            raise serializers.ValidationError(
                "Номер телефона должен содержать только цифры и знак '+'"
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
