"""Tests for User endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test data
test_user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123!"
}

test_user_update = {
    "username": "updateduser",
    "email": "updated@example.com"
}


class TestUserRegistration:
    """Test user registration"""

    def test_register_new_user(self):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json=test_user_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data

    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register with same email
        duplicate_user = {
            "username": "differentuser",
            "email": test_user_data["email"],
            "password": "Password123!"
        }
        response = client.post("/api/v1/auth/register", json=duplicate_user)
        assert response.status_code == 400


class TestUserLogin:
    """Test user login"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test user"""
        client.post("/api/v1/auth/register", json=test_user_data)

    def test_login_success(self):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self):
        """Test login with invalid password"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent",
                "password": "Password123!"
            }
        )
        assert response.status_code == 401


class TestUserProfile:
    """Test user profile operations"""

    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        client.post("/api/v1/auth/register", json=test_user_data)
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        return response.json()["access_token"]

    def test_get_current_user(self, auth_token):
        """Test getting current user profile"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]

    def test_update_profile(self, auth_token):
        """Test updating user profile"""
        response = client.put(
            "/api/v1/users/me",
            json=test_user_update,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_update["username"]
        assert data["email"] == test_user_update["email"]

    def test_get_user_without_auth(self):
        """Test accessing user endpoint without authentication"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 403


class TestTokenRefresh:
    """Test token refresh"""

    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        client.post("/api/v1/auth/register", json=test_user_data)
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        return response.json()["access_token"]

    def test_refresh_token(self, auth_token):
        """Test token refresh"""
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
