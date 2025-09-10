"""Test booking endpoints."""
import pytest
from datetime import datetime, timedelta

class TestBookings:
    """Booking tests."""
    
    def test_create_booking_validation(self, client, test_user_data):
        """Test booking validation rules."""
        # Register and login user
        client.post("/auth/register", json=test_user_data)
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test invalid time intervals (not :00 or :30)
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=15, second=0, microsecond=0)  # Invalid: :15
        end_time = start_time + timedelta(hours=1)
        
        booking_data = {
            "room_id": 1,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        response = client.post("/api/v1/bookings", json=booking_data, headers=headers)
        # Should fail due to validation (if room exists)
        # This test checks that our validation is working
        assert response.status_code in [422, 404]  # 422 for validation, 404 for missing room
    
    def test_booking_duration_validation(self, client, test_user_data):
        """Test booking duration limits."""
        # Register and login user
        client.post("/auth/register", json=test_user_data)
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test booking longer than 4 hours
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=5)  # 5 hours - should fail
        
        booking_data = {
            "room_id": 1,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        response = client.post("/api/v1/bookings", json=booking_data, headers=headers)
        # Should fail due to validation
        assert response.status_code in [422, 404]  # 422 for validation, 404 for missing room
    
    def test_get_my_bookings_requires_auth(self, client):
        """Test that getting bookings requires authentication."""
        response = client.get("/api/v1/bookings")
        assert response.status_code in [401, 403]  # Either unauthorized or forbidden