from rest_framework import generics
from rest_framework.permissions import AllowAny
from users.serializers import UserSerializer


class UserCreateView(generics.CreateAPIView):
    """
    Представление для создания нового пользователя (регистрация).
    Доступно для всех пользователей без аутентификации.
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
