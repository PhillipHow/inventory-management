"""
Pytest configuration and fixtures for backend API tests.
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add server directory to path
server_path = Path(__file__).parent.parent.parent / "server"
sys.path.insert(0, str(server_path))

from main import app


# Demo credentials shipped in server/data/users.json
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"


@pytest.fixture
def auth_token():
    """Obtain a valid JWT access token for the demo admin user."""
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/auth/login",
            json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        )
        assert response.status_code == 200, "Login failed in test setup"
        return response.json()["access_token"]


@pytest.fixture
def client(auth_token):
    """Authenticated test client — sends a valid Bearer token on every request.

    All /api routes now require authentication, so the default client fixture
    is pre-authenticated to keep endpoint tests focused on their own behavior.
    """
    with TestClient(app) as test_client:
        test_client.headers.update({"Authorization": f"Bearer {auth_token}"})
        yield test_client


@pytest.fixture
def unauthenticated_client():
    """Test client with no auth header — for testing the auth boundary itself."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_inventory_item():
    """Sample inventory item for testing."""
    return {
        "id": "1",
        "sku": "PCB-001",
        "name": "Single Layer PCB Assembly",
        "category": "Circuit Boards",
        "warehouse": "San Francisco",
        "quantity_on_hand": 450,
        "reorder_point": 200,
        "unit_cost": 24.99,
        "location": "Warehouse A-12",
        "last_updated": "2025-09-30T10:30:00"
    }


@pytest.fixture
def sample_order():
    """Sample order for testing."""
    return {
        "id": "1",
        "order_number": "ORD-2025-0001",
        "customer": "MegaCorp Industries",
        "items": [
            {
                "sku": "SPR-602",
                "name": "Compression Spring",
                "quantity": 981,
                "unit_price": 89.5
            }
        ],
        "status": "Delivered",
        "warehouse": "Tokyo",
        "category": "Sensors",
        "order_date": "2025-01-08T10:19:00",
        "expected_delivery": "2025-01-21T10:19:00",
        "total_value": 87799.5,
        "actual_delivery": "2025-01-20T10:19:00"
    }
