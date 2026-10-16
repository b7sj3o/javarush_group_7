import copy

import pytest
from fastapi.testclient import TestClient

from main import app
from models import books_db, orders_db, users_db


ADMIN = {"username": "admin@library.ua", "password": "admin12345"}
MANAGER = {"username": "manager@library.ua", "password": "manager12345"}
READER = {"username": "olia@example.com", "password": "secret123"}


@pytest.fixture(scope="module")
def client():
    """ Фікстура для створення TestClient. """
    with TestClient(app) as c:
        yield c
        
        
@pytest.fixture(autouse=True)
def fresh_db():
    """Кожен тест починає зі стартових даних і не лишає слідів наступному."""
    snapshot = copy.deepcopy((users_db, books_db, orders_db))
    yield
    for db, saved in zip((users_db, books_db, orders_db), snapshot, strict=True):
        db.clear()
        db.update(saved)


@pytest.fixture
def login(client):
    """Фабрика: логін через /token і клієнт, який уже носить заголовок Authorization."""

    def _login(credentials: dict) -> TestClient:
        response = client.post("/token", data=credentials)
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        return TestClient(app, headers={"Authorization": f"Bearer {token}"})

    return _login


@pytest.fixture
def admin_client(login):
    return login(ADMIN)


@pytest.fixture
def manager_client(login):
    return login(MANAGER)


@pytest.fixture
def reader_client(login):
    return login(READER)