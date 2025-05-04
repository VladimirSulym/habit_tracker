from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.serializers import UserSerializer

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты для модели User"""

    def setUp(self):
        self.user_data = {
            'email': 'test@ya.ru',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+79991234567',
            'city': 'Москва',
        }
        self.user = User.objects.create(**self.user_data)
        self.user.set_password('testpassword123')
        self.user.save()

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertEqual(self.user.first_name, self.user_data['first_name'])
        self.assertEqual(self.user.last_name, self.user_data['last_name'])
        self.assertEqual(self.user.phone, self.user_data['phone'])
        self.assertEqual(self.user.city, self.user_data['city'])
        # self.assertTrue(self.user.check_password(self.user_data['password']))

    def test_user_str_representation(self):
        """Тест строкового представления пользователя"""
        self.assertEqual(str(self.user), f"{self.user.last_name} {self.user.first_name}")

        # Тест когда first_name и last_name не указаны
        user_without_name = User.objects.create(
            email='noname@example.com',
        )
        user_without_name.set_password('testpassword123')
        user_without_name.save()
        self.assertEqual(str(user_without_name), user_without_name.email)


class UserSerializerTest(TestCase):
    """Тесты для UserSerializer"""

    def setUp(self):
        self.user_data = {
            'email': 'test@ya.ru',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+79991234567',
            'city': 'Москва',
        }

    def test_serializer_validation(self):
        """Тест корректности валидации данных сериализатором"""
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())

        # Тест некорректного номера телефона
        invalid_data = self.user_data.copy()
        invalid_data['phone'] = 'not-a-phone-number'
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone', serializer.errors)


class UserCreateViewTest(APITestCase):
    """Тесты для UserCreateView"""

    def setUp(self):
        self.url = reverse('users:user-register')
        self.user_data = {
            'email': 'test@ya.ru',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+79991234567',
            'city': 'Москва',
        }

    def test_create_user(self):
        """Тест создания пользователя через API"""
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_create_user_with_invalid_data(self):
        """Тест неудачного создания пользователя с некорректными данными"""
        # Отсутствует обязательное поле (email)
        invalid_data = self.user_data.copy()
        invalid_data.pop('email')
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Некорректный номер телефона
        invalid_data = self.user_data.copy()
        invalid_data['phone'] = 'not-a-phone-number'
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
