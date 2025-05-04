from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Модель пользователя, расширяющая стандартную модель Django AbstractUser.
    
    Заменяет поле username на email в качестве основного идентификатора.
    Добавляет дополнительные поля: телефон и город.
    """
    username = None
    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта",
        help_text="Адрес электронной почты пользователя",
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        help_text="Номер телефона пользователя",
        null=True,
        blank=True,
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Город",
        help_text="Город проживания пользователя",
        null=True,
        blank=True,
    )
    tg_chat_id = models.CharField(
        max_length=100,
        verbose_name="Tелеграм чат ID",
        help_text="Tелеграм чат ID",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = [
            "email",
        ]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        """
        Возвращает строковое представление пользователя.
        Если указаны фамилия и имя, возвращает их, иначе возвращает email.
        """
        if self.last_name and self.first_name:
            return f"{self.last_name} {self.first_name}"
        return self.email
