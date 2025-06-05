from django.test import Client
from django.contrib.auth import get_user_model
import json

User = get_user_model()


def create_authenticated_client(user_role='manager', **user_kwargs):
    """Создает аутентифицированный клиент"""
    if user_role == 'owner':
        user = User.objects.create_user(
            username='test_owner',
            password='testpass123',
            role='owner',
            **user_kwargs
        )
    elif user_role == 'manager':
        user = User.objects.create_user(
            username='test_manager',
            password='testpass123',
            role='manager',
            **user_kwargs
        )
    else:  # installer
        user = User.objects.create_user(
            username='test_installer',
            password='testpass123',
            role='installer',
            **user_kwargs
        )
    
    client = Client()
    client.login(username=user.username, password='testpass123')
    client.user = user  # Добавляем ссылку на пользователя
    return client


def api_client_with_auth(user):
    """Создает API клиент с аутентификацией"""
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def assert_response_contains_fields(response, required_fields):
    """Проверяет наличие обязательных полей в JSON ответе"""
    if hasattr(response, 'data'):
        data = response.data
    else:
        data = json.loads(response.content)
    
    for field in required_fields:
        assert field in data, f"Field '{field}' not found in response"


def create_test_order_with_items(manager, installer, client=None):
    """Создает тестовый заказ с позициями"""
    from tests.conftest import BaseTestCase
    base_test = BaseTestCase()
    base_test.setUpTestData()
    
    if client is None:
        client = base_test.customer
    
    return base_test.create_completed_order_with_items(manager, installer)