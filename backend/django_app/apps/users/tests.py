import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "test@mail.com",
        "password": "testpass123",
        "password2": "testpass123",
    }


@pytest.mark.django_db
def test_register_success(client, user_data):
    response = client.post("/api/auth/register/", user_data, format="json")
    assert response.status_code == 201
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_register_wrong_password(client, user_data):
    user_data["password2"] = "wrongpassword"
    response = client.post("/api/auth/register/", user_data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_duplicate_email(client, user_data):
    client.post("/api/auth/register/", user_data, format="json")
    response = client.post("/api/auth/register/", user_data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_success(client, user_data):
    client.post("/api/auth/register/", user_data, format="json")
    response = client.post(
        "/api/auth/login/",
        {"username": "testuser", "password": "testpass123"},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_register_duplicate_username(client, user_data):
    client.post("/api/auth/register/", user_data, format="json")
    user_data["email"] = "other@mail.com"
    response = client.post("/api/auth/register/", user_data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_invalid_email(client, user_data):
    user_data["email"] = "notanemail"
    response = client.post("/api/auth/register/", user_data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_wrong_password(client, user_data):
    client.post("/api/auth/register/", user_data, format="json")
    response = client.post(
        "/api/auth/login/",
        {"username": "testuser", "password": "wrongpassword"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_login_nonexistent_user(client):
    response = client.post(
        "/api/auth/login/",
        {"username": "nobody", "password": "testpass123"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_register_missing_fields(client):
    response = client.post("/api/auth/register/", {}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_token_refresh(client, user_data):
    client.post("/api/auth/register/", user_data, format="json")
    login = client.post(
        "/api/auth/login/",
        {"username": "testuser", "password": "testpass123"},
        format="json",
    )
    refresh = login.data["refresh"]
    response = client.post(
        "/api/auth/token/refresh/",
        {"refresh": refresh},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_token_refresh_invalid(client):
    response = client.post(
        "/api/auth/token/refresh/",
        {"refresh": "wrong_refresh"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_logout_success(client, user_data):
    client.post("/api/auth/register/", user_data, format="json")

    login = client.post(
        "/api/auth/login/",
        {"username": "testuser", "password": "testpass123"},
        format="json",
    )

    refresh = login.data["refresh"]

    response = client.post(
        "/api/auth/logout/",
        {"refresh": refresh},
        format="json",
    )

    assert response.status_code == 205


@pytest.mark.django_db
def test_logout_invalid_token(client):
    response = client.post(
        "/api/auth/logout/", {"refresh": "wrong_refresh"}, format="json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_logout_without_token(client):
    response = client.post(
        "/api/auth/logout/",
        {},
        format="json",
    )

    assert response.status_code == 400
