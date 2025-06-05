import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from customer_clients.models import Client as CustomerClient
from services.models import Service
from orders.models import Order, OrderItem
from finance.models import Transaction
from decimal import Decimal

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Фабрика для создания пользователей"""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    role = 'manager'
    phone = factory.Faker('phone_number')
    
    @factory.post_generation
    def set_password(obj, create, extracted, **kwargs):
        if create:
            obj.set_password('testpass123')
            obj.save()


class OwnerFactory(UserFactory):
    """Фабрика для создания владельца"""
    role = 'owner'
    username = 'owner'


class ManagerFactory(UserFactory):
    """Фабрика для создания менеджера"""
    role = 'manager'


class InstallerFactory(UserFactory):
    """Фабрика для создания монтажника"""
    role = 'installer'


class CustomerClientFactory(DjangoModelFactory):
    """Фабрика для создания клиентов"""
    class Meta:
        model = CustomerClient
    
    name = factory.Faker('name')
    address = factory.Faker('address')
    phone = factory.Faker('phone_number')
    source = factory.Iterator(['website', 'avito', 'vk', 'recommendations', 'other'])


class ServiceFactory(DjangoModelFactory):
    """Фабрика для создания услуг"""
    class Meta:
        model = Service
    
    name = factory.Faker('catch_phrase')
    cost_price = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    selling_price = factory.LazyAttribute(lambda obj: obj.cost_price * Decimal('1.5'))
    category = factory.Iterator(['conditioner', 'installation', 'dismantling', 'maintenance', 'additional'])


class OrderFactory(DjangoModelFactory):
    """Фабрика для создания заказов"""
    class Meta:
        model = Order
    
    client = factory.SubFactory(CustomerClientFactory)
    manager = factory.SubFactory(ManagerFactory)
    status = 'new'


class OrderItemFactory(DjangoModelFactory):
    """Фабрика для создания позиций заказа"""
    class Meta:
        model = OrderItem
    
    order = factory.SubFactory(OrderFactory)
    service = factory.SubFactory(ServiceFactory)
    price = factory.LazyAttribute(lambda obj: obj.service.selling_price)
    seller = factory.SubFactory(UserFactory)


class TransactionFactory(DjangoModelFactory):
    """Фабрика для создания транзакций"""
    class Meta:
        model = Transaction
    
    type = factory.Iterator(['income', 'expense'])
    amount = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    description = factory.Faker('sentence')