"""Test authentication endpoints."""
import pytest

class TestAuth:
    """Authentication tests."""
    
    def test_register_user(self, client, test_user_data):
        """Test user registration."""
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["is_admin"] == test_user_data["is_admin"]
    
    def test_register_duplicate_user(self, client, test_user_data):
        """Test registering duplicate user fails."""
        # Register first user
        client.post("/auth/register", json=test_user_data)
        
        # Try to register same user again
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_login_valid_user(self, client, test_user_data):
        """Test login with valid credentials."""
        # Register user first
        client.post("/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user_email"] == test_user_data["email"]
    
    def test_login_invalid_credentials(self, client, test_user_data):
        """Test login with invalid credentials."""
        # Register user first
        client.post("/auth/register", json=test_user_data)
        
        # Try login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_protected_endpoint_without_token(self, client):
        """Test protected endpoint without authentication."""
        response = client.get("/protected")
        assert response.status_code in [401, 403]  # Either unauthorized or forbidden
    
    def test_protected_endpoint_with_token(self, client, test_user_data):
        """Test protected endpoint with valid token."""
        # Register and login user
        client.post("/auth/register", json=test_user_data)
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/protected", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert test_user_data["email"] in data["message"]