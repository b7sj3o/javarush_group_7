from config import settings
from dependencies import get_current_user
from main import app
from models import Role, User, get_user_by_email, users_db
from security import decode_token

READER = {"username": "olia@example.com", "password": "secret123"}


# ---------- /token ----------


def test_login_ok(client):
    response = client.post("/token", data=READER)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2  # header.payload.signature


def test_token_payload(client):
    token = client.post("/token", data=READER).json()["access_token"]
    payload = decode_token(token)
    assert payload["sub"] == "olia@example.com"
    assert payload["role"] == "reader"
    assert "exp" in payload


def test_login_wrong_password(client):
    response = client.post("/token", data={**READER, "password": "wrong"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_login_unknown_user(client):
    response = client.post("/token", data={"username": "nobody@example.com", "password": "secret123"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}  # не виказуємо, чи є такий email


def test_login_inactive_user(client):
    response = client.post("/token", data={"username": "off@example.com", "password": "secret123"})
    assert response.status_code == 403
    assert response.json() == {"detail": "User is inactive"}


def test_login_needs_form_not_json(client):
    # Типова помилка клієнта: OAuth2 password flow приймає form-data, а не JSON
    response = client.post("/token", json=READER)
    assert response.status_code == 422


# ---------- Захищений ендпоінт (слайд 8) ----------


def test_protected_no_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_protected_invalid_token(client):
    response = client.get("/users/me", headers={"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_protected_tampered_token(client):
    token = client.post("/token", data=READER).json()["access_token"]
    header, payload, signature = token.split(".")
    response = client.get("/users/me", headers={"Authorization": f"Bearer {header}.{payload}.{signature[:-3]}abc"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_protected_expired_token(client, monkeypatch):
    monkeypatch.setattr(settings, "access_token_expire_minutes", -1)  # токен народжується простроченим
    token = client.post("/token", data=READER).json()["access_token"]
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Token expired"}


def test_protected_deleted_user(client):
    token = client.post("/token", data=READER).json()["access_token"]
    del users_db[get_user_by_email("olia@example.com").id]  # fresh_db поверне її після тесту
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "User not found"}


def test_protected_valid_token(client):
    token = client.post("/token", data=READER).json()["access_token"]
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "olia@example.com"
