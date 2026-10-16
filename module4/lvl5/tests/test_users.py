import pytest

from tests.conftest import READER


def test_list_users_success(admin_client):
    response = admin_client.get("/users")
    
    assert response.status_code == 200
    assert len(response.json()) == 4
    
    
def test_list_users_error(client):
    response = client.get("/users")
    
    assert response.status_code == 401
    
NEW_USER={
    "name": "Тест",
    "email": "test@example.com",
    "password": "password1",
    "password_confirm": "password1",
}
    
def test_register_success(client):
    response = client.post("/users", json=NEW_USER)
    assert response.status_code == 201
    user = response.json()
    assert user["name"] == "Тест"
    assert user["email"] == "test@example.com"
    assert user["role"] == "reader"
    assert user["is_active"] is True
    assert "password" not in user and "hashed_password" not in user
    
    
def test_register_duplicate_email(client):
    assert client.post("/users", json=NEW_USER).status_code == 201
    response = client.post("/users", json={**NEW_USER, "email": "TEST@example.com"})
    assert response.status_code == 409
    assert response.json() == {"detail": "Такий email вже зайнятий"}
    
    
def test_register_then_login(client):
    client.post("/users", json=NEW_USER)
    response = client.post("/token", data={"username": "test@example.com", "password": "password1"})
    assert response.status_code == 200
    
    

@pytest.mark.parametrize(
    "payload, loc",
    [
        ({**NEW_USER, "email": "not-an-email"}, ["body", "email"]),
        ({**NEW_USER, "password": "short", "password_confirm": "short"}, ["body", "password"]),
        ({**NEW_USER, "name": "A"}, ["body", "name"]),
        ({**NEW_USER, "role": "admin"}, ["body", "role"]),  # extra="forbid": роль собі не призначиш
        ({**NEW_USER, "password_confirm": "password2"}, ["body"]),  # model_validator
    ],
)
def test_register_invalid(client, payload, loc):
    response = client.post("/users", json=payload)
    assert response.status_code == 422
    assert loc in [error["loc"] for error in response.json()["detail"]]
    
    

def test_me(reader_client):
    response = reader_client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["email"] == "olia@example.com"
    assert response.json()["role"] == "reader"


def test_update_my_name(reader_client):
    response = reader_client.patch("/users/me", json={"name": "Ольга"})
    assert response.status_code == 200
    assert response.json()["name"] == "Ольга"
    assert reader_client.get("/users/me").json()["name"] == "Ольга"


def test_change_password(reader_client, client):
    payload = {"old_password": "secret123", "new_password": "newsecret1", "new_password_confirm": "newsecret1"}
    assert reader_client.post("/users/me/password", json=payload).status_code == 204
    assert client.post("/token", data=READER).status_code == 401
    assert client.post("/token", data={**READER, "password": "newsecret1"}).status_code == 200


def test_change_password_wrong_old(reader_client):
    payload = {"old_password": "wrong", "new_password": "newsecret1", "new_password_confirm": "newsecret1"}
    response = reader_client.post("/users/me/password", json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Неправильний старий пароль"}