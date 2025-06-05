import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from customer_clients.models import Client as CustomerClient
from services.models import Service
from orders.models import Order, OrderItem
from finance.models import Transaction
from decimal import Decimal
from django.utils import timezone

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс для всех тестов с общими методами"""
    
    @classmethod
    def setUpTestData(cls):
        """Создание общих тестовых данных"""
        # Создаем пользователей разных ролей
        cls.owner = User.objects.create_user(
            username='test_owner',
            password='testpass123',
            role='owner',
            first_name='Владелец',
            last_name='Тестовый'
        )
        
        cls.manager = User.objects.create_user(
            username='test_manager',
            password='testpass123',
            role='manager',
            first_name='Менеджер',
            last_name='Тестовый'
        )
        
        cls.installer = User.objects.create_user(
            username='test_installer',
            password='testpass123',
            role='installer',
            first_name='Монтажник',
            last_name='Тестовый'
        )
        
        # Создаем тестового клиента
        cls.customer = CustomerClient.objects.create(
            name='Тестовый Клиент',
            address='ул. Тестовая, д. 123',
            phone='+7900123456',
            source='website'
        )
        
        # Создаем тестовые услуги
        cls.conditioner_service = Service.objects.create(
            name='Кондиционер Samsung 12000 BTU',
            cost_price=Decimal('20000.00'),
            selling_price=Decimal('35000.00'),
            category='conditioner'
        )
        
        cls.installation_service = Service.objects.create(
            name='Монтаж кондиционера',
            cost_price=Decimal('2000.00'),
            selling_price=Decimal('5000.00'),
            category='installation'
        )
        
        cls.additional_service = Service.objects.create(
            name='Чистка фильтров',
            cost_price=Decimal('500.00'),
            selling_price=Decimal('2000.00'),
            category='additional'
        )
    
    def create_test_order(self, client=None, manager=None, installers=None, items=None):
        """Вспомогательный метод для создания тестового заказа"""
        if client is None:
            client = self.customer
        if manager is None:
            manager = self.manager
        
        order = Order.objects.create(
            client=client,
            manager=manager,
            status='new'
        )
        
        if installers:
            order.installers.set(installers)
        else:
            order.installers.add(self.installer)
        
        # Добавляем позиции, если указаны
        if items:
            for item_data in items:
                OrderItem.objects.create(
                    order=order,
                    service=item_data.get('service', self.installation_service),
                    price=item_data.get('price', Decimal('5000.00')),
                    seller=item_data.get('seller', manager)
                )
        
        return order
    
    def create_completed_order_with_items(self, manager=None, installer=None):
        """Создает завершенный заказ с позициями для тестирования расчетов"""
        if manager is None:
            manager = self.manager
        if installer is None:
            installer = self.installer
        
        order = Order.objects.create(
            client=self.customer,
            manager=manager,
            status='completed',
            completed_at=timezone.now()
        )
        order.installers.add(installer)
        
        # Добавляем позиции разных категорий
        items = [
            {
                'service': self.conditioner_service,
                'price': Decimal('35000.00'),
                'seller': manager
            },
            {
                'service': self.installation_service,
                'price': Decimal('5000.00'),
                'seller': manager
            },
            {
                'service': self.additional_service,
                'price': Decimal('2000.00'),
                'seller': installer
            }
        ]
        
        for item_data in items:
            OrderItem.objects.create(order=order, **item_data)
        
        return order
    
    def assertDecimalEqual(self, first, second, places=2):
        """Сравнение Decimal значений с округлением"""
        first_rounded = round(first, places)
        second_rounded = round(second, places)
        self.assertEqual(first_rounded, second_rounded)