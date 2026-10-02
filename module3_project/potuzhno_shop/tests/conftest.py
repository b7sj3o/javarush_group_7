import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from apps.accounts.models import Profile
from apps.api.permissions import CATALOG_MANAGER_GROUP
from apps.catalog.models import Brand, Category, Product

User = get_user_model()


@pytest.fixture
def api_client():
    """ Фікстура для створення екземпляра APIClient """
    return APIClient()


@pytest.fixture
def category(db):
    return Category.objects.create(name="Худі", slug="hoodies")


@pytest.fixture
def brand(db):
    return Brand.objects.create(name="Reebok", slug="reebok")


@pytest.fixture
def product(db, category, brand):
    return Product.objects.create(
        name="Худі Oversize",
        slug="hudi-oversize",
        price="1290.00",
        stock=10,
        audience="unisex",
        category=category,
        brand=brand,
    )


@pytest.fixture
def user(db):
    account = User.objects.create_user(username="buyer", password="pass12345")
    Profile.objects.get_or_create(user=account)
    return account


@pytest.fixture
def catalog_manager(db):
    account = User.objects.create_user(username="manager", password="pass12345")
    Profile.objects.get_or_create(user=account)
    group, _ = Group.objects.get_or_create(name=CATALOG_MANAGER_GROUP)
    account.groups.add(group)
    return account


