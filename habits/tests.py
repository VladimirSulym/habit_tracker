from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch
import datetime

from habits.models import Habit
from habits.serializers import HabitSerializer
from habits.services import send_message_telegram

User = get_user_model()


class HabitModelTest(TestCase):
    """Тесты для модели Habit"""

    def setUp(self):
        # Очистка всех привычек для изоляции тестов
        Habit.objects.all().delete()
        User.objects.all().delete()

        self.user = User.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.user.set_password('testpassword123')
        self.user.save()

        self.habit_data = {
            'user': self.user,
            'place': 'Дом',
            'date': timezone.now().date(),
            'action': 'Пить воду',
            'frequency': 1,
            'execution_time': 60,
            'reward': 'Чувствовать себя хорошо',
        }

        self.habit = Habit.objects.create(**self.habit_data)

        # Создание приятной привычки для тестирования связанных привычек 
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            date=timezone.now().date(),
            action='Слушать музыку',
            frequency=1,
            execution_time=60,
            is_pleasant=True
        )

    def test_habit_creation(self):
        """Тест создания привычки"""
        self.assertEqual(Habit.objects.count(), 2)  # Включая приятную привычку
        self.assertEqual(self.habit.place, self.habit_data['place'])
        self.assertEqual(self.habit.action, self.habit_data['action'])
        self.assertEqual(self.habit.frequency, self.habit_data['frequency'])
        self.assertEqual(self.habit.execution_time, self.habit_data['execution_time'])
        self.assertEqual(self.habit.reward, self.habit_data['reward'])
        self.assertEqual(self.habit.user, self.user)

    def test_habit_str_representation(self):
        """Тест строкового представления привычки"""
        expected_str = f"Привычка {self.habit.action} в {self.habit.date}"
        self.assertEqual(str(self.habit), expected_str)

    def test_habit_validation_execution_time(self):
        """Тест валидации времени выполнения"""
        with self.assertRaises(Exception):
            Habit.objects.create(
                user=self.user,
                place='Дом',
                date=timezone.now().date(),
                action='Бегать',
                frequency=1,
                execution_time=121,  # Больше 120 секунд
                reward='Чувствовать себя хорошо'
            )

    def test_habit_validation_frequency(self):
        """Тест валидации частоты выполнения"""
        with self.assertRaises(Exception):
            Habit.objects.create(
                user=self.user,
                place='Дом',
                date=timezone.now().date(),
                action='Бегать',
                frequency=8,  # Больше 7 дней
                execution_time=60,
                reward='Чувствовать себя хорошо'
            )

    def test_pleasant_habit_validation(self):
        """Тест валидации приятных привычек"""
        with self.assertRaises(Exception):
            Habit.objects.create(
                user=self.user,
                place='Дом',
                date=timezone.now().date(),
                action='Смотреть ТВ',
                frequency=1,
                execution_time=60,
                is_pleasant=True,
                reward='Не разрешено для приятных привычек'
            )

    def test_related_habit_validation(self):
        """Тест валидации связанных привычек"""
        # Проверка того, что связанная привычка должна быть приятной
        non_pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            date=timezone.now().date(),
            action='Читать книгу',
            frequency=1,
            execution_time=60,
            reward='Чувствовать себя хорошо'
        )

        with self.assertRaises(Exception):
            Habit.objects.create(
                user=self.user,
                place='Дом',
                date=timezone.now().date(),
                action='Учиться',
                frequency=1,
                execution_time=60,
                related_habit=non_pleasant_habit  # Неприятная привычка
            )

        # Проверка того, что привычка может иметь приятную связанную привычку
        valid_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            date=timezone.now().date(),
            action='Учиться',
            frequency=1,
            execution_time=60,
            related_habit=self.pleasant_habit  # Приятная привычка
        )
        self.assertEqual(valid_habit.related_habit, self.pleasant_habit)

    def test_reward_or_related_habit_required(self):
        """Тест требования наличия награды или связанной привычки для неприятных привычек"""
        with self.assertRaises(Exception):
            Habit.objects.create(
                user=self.user,
                place='Дом',
                date=timezone.now().date(),
                action='Учиться',
                frequency=1,
                execution_time=60,
                # Нет награды или связанной привычки
            )


class HabitSerializerTest(TestCase):
    """Тесты для HabitSerializer"""

    def setUp(self):
        # Очистка всех привычек для изоляции тестов
        Habit.objects.all().delete()
        User.objects.all().delete()

        self.user = User.objects.create(
            email='test@example.com',
        )
        self.user.set_password('testpassword123')
        self.user.save()

        self.habit_data = {
            'place': 'Дом',
            'date': timezone.now().date().isoformat(),
            'action': 'Пить воду',
            'frequency': 1,
            'execution_time': 60,
            'reward': 'Чувствовать себя хорошо',
            'is_public': False
        }

    def test_serializer_validation(self):
        """Тест корректности валидации данных сериализатором"""
        serializer = HabitSerializer(data=self.habit_data)
        serializer.context['request'] = type('obj', (object,), {'user': self.user})
        self.assertTrue(serializer.is_valid())


class HabitViewsTest(APITestCase):
    """Тесты для представлений Habit"""

    def setUp(self):
        # Очистка всех привычек для изоляции тестов
        Habit.objects.all().delete()
        User.objects.all().delete()

        self.user = User.objects.create(
            email='test@example.com',
        )
        self.user.set_password('testpassword123')
        self.user.save()

        self.other_user = User.objects.create(
            email='other@example.com',
        )
        self.other_user.set_password('testpassword123')
        self.other_user.save()

        self.client.force_authenticate(user=self.user)

        self.habit_data = {
            'place': 'Дом',
            'date': timezone.now().date().isoformat(),
            'action': 'Пить воду',
            'frequency': 1,
            'execution_time': 60,
            'reward': 'Чувствовать себя хорошо',
            'is_public': False
        }

        # Создание привычки для пользователя
        self.habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            date=timezone.now().date(),
            action='Пить воду',
            frequency=1,
            execution_time=60,
            reward='Чувствовать себя хорошо'
        )

        # Создание публичной привычки для другого пользователя
        self.public_habit = Habit.objects.create(
            user=self.other_user,
            place='Тренажерный зал',
            date=timezone.now().date(),
            action='Упражнения',
            frequency=2,
            execution_time=30,
            reward='Здоровье',
            is_public=True
        )

        # Создание приватной привычки для другого пользователя
        self.private_habit = Habit.objects.create(
            user=self.other_user,
            place='Дом',
            date=timezone.now().date(),
            action='Читать',
            frequency=1,
            execution_time=20,
            reward='Знания',
            is_public=False
        )

    def test_habit_list_create_view(self):
        """Тест HabitListCreateView"""
        url = reverse('habits:habit-list-create')

        # Тест GET - должен возвращать привычки пользователя
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Тест POST - должен создать новую привычку для пользователя
        response = self.client.post(url, self.habit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(user=self.user).count(), 2)
        self.assertEqual(response.data['action'], self.habit_data['action'])

    def test_public_habit_list_view(self):
        """Тест PublicHabitListView"""
        url = reverse('habits:public-habits')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_habit_detail_view(self):
        """Тест HabitDetailView"""
        # Тест собственной привычки пользователя
        url = reverse('habits:habit-detail', args=[self.habit.id])

        # Тест GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], self.habit.action)

        # Тест PUT
        updated_data = {
            'place': 'Офис',
            'date': timezone.now().date().isoformat(),
            'action': 'Пить больше воды',
            'frequency': 1,
            'execution_time': 60,
            'reward': 'Чувствовать себя лучше',
            'is_public': False
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, 'Пить больше воды')

        # Тест DELETE
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(id=self.habit.id).count(), 0)

        # Тест публичной привычки другого пользователя - должна быть доступна
        url = reverse('habits:habit-detail', args=[self.public_habit.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Тест приватной привычки другого пользователя - не должна быть доступна
        url = reverse('habits:habit-detail', args=[self.private_habit.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class HabitPermissionsTest(APITestCase):
    """Тесты для прав доступа Habit"""

    def setUp(self):
        # Очистка всех привычек для изоляции тестов
        Habit.objects.all().delete()
        User.objects.all().delete()

        self.user = User.objects.create(
            email='test@example.com',
        )
        self.user.set_password('testpassword123')
        self.user.save()

        self.other_user = User.objects.create(
            email='other@example.com',
        )
        self.other_user.set_password('testpassword123')
        self.other_user.save()

        # Создание привычки для другого пользователя
        self.other_user_habit = Habit.objects.create(
            user=self.other_user,
            place='Дом',
            date=timezone.now().date(),
            action='Read',
            frequency=1,
            execution_time=20,
            reward='Знания',
            is_public=True  # Публичная, чтобы наш пользователь мог ее видеть
        )

    def test_owner_or_read_only_permission(self):
        """Тест разрешения IsOwnerOrReadOnly"""
        self.client.force_authenticate(user=self.user)
        url = reverse('habits:habit-detail', args=[self.other_user_habit.id])

        # Тест GET - должен быть разрешен для публичных привычек
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Тест PUT - не должен быть разрешен для привычек других пользователей
        updated_data = {
            'place': 'Офис',
            'date': timezone.now().date().isoformat(),
            'action': 'Изменено другим пользователем',
            'frequency': 1,
            'execution_time': 20,
            'reward': 'Измененное вознаграждение',
            'is_public': True
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Тест DELETE - не должен быть разрешен для привычек других пользователей
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class HabitServicesTest(TestCase):
    """Тесты для сервисов Habit"""

    @patch('habits.services.requests.get')
    def test_send_message_telegram(self, mock_get):
        """Тест функции send_message_telegram"""
        # Настройка мока
        mock_get.return_value.status_code = 200

        # Вызов функции
        message = "Test message"
        chat_id = "123456789"
        send_message_telegram(message, chat_id)

        # Проверка, что мок был вызван с правильными параметрами
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn('sendMessage', args[0])
        self.assertEqual(kwargs['params']['text'], message)
        self.assertEqual(kwargs['params']['chat_id'], chat_id)
