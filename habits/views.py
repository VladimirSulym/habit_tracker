from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from habits.models import Habit
from habits.serializers import HabitSerializer
from habits.permissions import IsOwnerOrReadOnly
from rest_framework.serializers import ValidationError


class HabitListCreateView(generics.ListCreateAPIView):
    """
    Представление для просмотра списка и создания привычек.
    Доступно только аутентифицированным пользователям.
    При просмотре отображаются только привычки текущего пользователя.
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            raise ValidationError(e.args[0])


class PublicHabitListView(generics.ListAPIView):
    """
    Представление для просмотра списка публичных привычек.
    Доступно только аутентифицированным пользователям.
    Отображает все привычки, помеченные как публичные.
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    queryset = Habit.objects.filter(is_public=True)


class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для просмотра, обновления и удаления отдельной привычки.
    Доступно только аутентифицированным пользователям.
    Пользователь может редактировать только свои привычки, но просматривать также и публичные.
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # Проверяем, является ли это запросом для генерации схемы
        if getattr(self, "swagger_fake_view", False):
            # Возвращаем пустой QuerySet для схемы
            return Habit.objects.none()

        # Основная логика для реальных запросов
        return Habit.objects.filter(user=self.request.user) | Habit.objects.filter(
            is_public=True
        )
