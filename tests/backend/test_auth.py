"""
Tests for authentication endpoints and the API auth boundary.
"""
import pytest


class TestAuthEndpoints:
    """Test suite for login and current-user endpoints."""

    def test_login_success(self, unauthenticated_client):
        """Valid credentials return a bearer access token."""
        response = unauthenticated_client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, unauthenticated_client):
        """Incorrect password is rejected with 401."""
        response = unauthenticated_client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrong-password"},
        )
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_unknown_user(self, unauthenticated_client):
        """Unknown username is rejected with 401."""
        response = unauthenticated_client.post(
            "/api/auth/login",
            json={"username": "nobody", "password": "whatever"},
        )
        assert response.status_code == 401

    def test_login_missing_fields(self, unauthenticated_client):
        """Missing required fields return a validation error."""
        response = unauthenticated_client.post(
            "/api/auth/login", json={"username": "admin"}
        )
        assert response.status_code == 422

    def test_me_returns_current_user(self, client):
        """Authenticated /me returns the user's profile."""
        response = client.get("/api/auth/me")
        assert response.status_code == 200

        data = response.json()
        assert data["username"] == "admin"
        assert data["full_name"] == "Admin User"
        assert data["role"] == "admin"

    def test_manager_can_login(self, unauthenticated_client):
        """The second demo user (manager) can also authenticate."""
        response = unauthenticated_client.post(
            "/api/auth/login",
            json={"username": "manager", "password": "manager123"},
        )
        assert response.status_code == 200


class TestAuthBoundary:
    """Test that data endpoints are protected."""

    def test_data_endpoint_requires_auth(self, unauthenticated_client):
        """Unauthenticated data requests are rejected with 401."""
        response = unauthenticated_client.get("/api/inventory")
        assert response.status_code == 401

    def test_invalid_token_rejected(self, unauthenticated_client):
        """A malformed/tampered token is rejected with 401."""
        response = unauthenticated_client.get(
            "/api/inventory",
            headers={"Authorization": "Bearer not.a.real.token"},
        )
        assert response.status_code == 401

    def test_valid_token_grants_access(self, client):
        """A valid token unlocks protected data endpoints."""
        response = client.get("/api/inventory")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_public_root_no_auth(self, unauthenticated_client):
        """The public root endpoint does not require auth."""
        response = unauthenticated_client.get("/")
        assert response.status_code == 200

    def test_login_endpoint_is_public(self, unauthenticated_client):
        """The login endpoint itself does not require auth."""
        response = unauthenticated_client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 200
