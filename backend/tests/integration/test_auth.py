import jwt
import pytest
from backend.api.main import app
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

client = TestClient(app)


def test_login_success(client, test_user):
    """Test successful login flow"""
    response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_me_endpoint(client, auth_headers):
    """Test accessing /me endpoint with valid token"""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == "test@example.com"
    assert user_data["first_name"] == "Test"
    assert user_data["last_name"] == "User"


def test_login_wrong_password(client, test_user):
    """Test login with incorrect password"""
    response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "wrongpassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


def test_me_without_token(client):
    """Test accessing /me endpoint without token"""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_invalid_token(client):
    """Test accessing /me endpoint with invalid token"""
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401


@pytest.mark.production_settings
def test_token_expiration_matches_production(client, test_user):
    """Verify token expiration matches production settings"""
    from backend.config.settings import ACCESS_TOKEN_EXPIRE_MINUTES

    response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = response.json()["access_token"]

    # Verify token expiration
    from backend.config.settings import JWT_SECRET_KEY, JWT_ALGORITHM

    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    created_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc) - timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    assert (exp_time - created_time).total_seconds() == ACCESS_TOKEN_EXPIRE_MINUTES * 60
