from django.db import models

from config.settings import AUTH_USER_MODEL
from rest_framework.serializers import ValidationError


class Habit(models.Model):
    """
    Модель привычки пользователя.
    
    Описывает привычку, которую пользователь хочет сформировать, включая место, время,
    периодичность выполнения, связанные привычки или вознаграждения.
    """

    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Пользователь, создавший привычку",
        db_index=True,
        related_name="habits",
    )
    place = models.CharField(
        max_length=255,
        verbose_name="Место выполнения",
        help_text="Место, где необходимо выполнять привычку",
    )
    date = models.DateField(
        help_text="Дата и время выполнения привычки",
        verbose_name="Дата и время выполнения привычки",
    )
    action = models.TextField(
        verbose_name="Действие",
        help_text="Действие, которое представляет из себя привычка",
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
        help_text="Отметьте, если привычка является приятной",
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с текущей привычкой",
    )
    frequency = models.IntegerField(
        default=1,
        verbose_name="Периодичность (в днях)",
        help_text="Периодичность выполнения привычки в днях",
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Вознаграждение",
        help_text="Вознаграждение за выполнение привычки",
    )
    execution_time = models.IntegerField(
        verbose_name="Время на выполнение (в минутах)",
        help_text="Время, необходимое на выполнение привычки, в минутах",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
        help_text="Отметьте, если привычка должна быть публичной",
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-date"]

    def __str__(self):
        """Возвращает строковое представление привычки"""
        return f"Привычка {self.action} в {self.date}"

    def clean(self):
        """
        Проверяет корректность данных привычки перед сохранением.
        
        Проверяются следующие условия:
        - Время выполнения не более 120 секунд
        - Периодичность от 1 до 7 дней
        - Приятная привычка не может иметь вознаграждение или связанную привычку
        - Нельзя одновременно указать вознаграждение и связанную привычку
        - Связанной может быть только приятная привычка
        - Должно быть указано вознаграждение или связанная привычка
        """
        # Проверка длительности выполнения
        if self.execution_time > 120:
            raise ValidationError("Время выполнения не должно превышать 120 секунд")

        # Проверка периодичности
        if self.frequency < 1 or self.frequency > 7:
            raise ValidationError("Периодичность должна быть от 1 до 7 дней")

        # Проверка: приятная привычка не может иметь вознаграждение или связанную привычку
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError(
                "Приятная привычка не может иметь вознаграждение или связанную привычку"
            )

        # Проверка: нельзя одновременно указать и вознаграждение и связанную привычку
        if self.reward and self.related_habit:
            raise ValidationError(
                "Нельзя одновременно указать и вознаграждение и связанную привычку"
            )

        # Проверка: в связанные привычки можно добавлять только приятные привычки
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError(
                "В связанные привычки можно добавлять только приятные привычки"
            )

        # Должно быть заполнено хотя бы одно поле - или вознаграждение, или связанная привычка
        if not self.is_pleasant and not self.reward and not self.related_habit:
            raise ValidationError(
                "Необходимо указать либо вознаграждение, либо связанную привычку"
            )

    def save(self, *args, **kwargs):
        """Сохраняет привычку, предварительно проверяя корректность данных"""
        self.full_clean()
        super().save(*args, **kwargs)
