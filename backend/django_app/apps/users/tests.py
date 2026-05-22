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
