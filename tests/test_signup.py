import pytest
import uuid
from fastapi.testclient import TestClient



def test_signup_duplicate_email(client):
    """Test that duplicate email returns 409 Conflict."""
    payload = {
        "name": "Ana",
        "email": "duplicate@example.com",
        "password": "S3cure!123",
        "display_name": "Ana G",
    }
    
    # First signup should succeed
    response1 = client.post("/signup", json=payload)
    assert response1.status_code == 201
    
    # Second signup with same email should fail
    response2 = client.post("/signup", json=payload)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"].lower()


def test_signup_with_idempotency_key(client):
    """Test idempotency key prevents duplicate processing."""
    payload = {
        "name": "Ana",
        "email": "idempotent@example.com",
        "password": "S3cure!123",
        "display_name": "Ana G",
    }
    
    idempotency_key = str(uuid.uuid4())
    headers = {"Idempotency-Key": idempotency_key}
    
    # First request
    response1 = client.post("/signup", json=payload, headers=headers)
    assert response1.status_code == 201
    data1 = response1.json()
    
    # Second request with same idempotency key should return cached response
    response2 = client.post("/signup", json=payload, headers=headers)
    assert response2.status_code == 201
    data2 = response2.json()
    
    assert data1["id"] == data2["id"]
    assert data1["email"] == data2["email"]
    assert response2.headers.get("X-Idempotency-Hit") == "true"


def test_signup_idempotency_key_conflict(client):
    """Test that same idempotency key with different payload returns 422."""
    idempotency_key = str(uuid.uuid4())
    
    # First request
    payload1 = {
        "name": "User One",
        "email": "user1@example.com",
        "password": "S3cure!123",
        "display_name": "User One",
    }
    response1 = client.post(
        "/signup",
        json=payload1,
        headers={"Idempotency-Key": idempotency_key}
    )
    assert response1.status_code == 201
    
    # Second request with same idempotency key but different payload
    payload2 = {
        "name": "User Two",
        "email": "user2@example.com",
        "password": "S3cure!123",
        "display_name": "User Two",
    }
    response2 = client.post(
        "/signup",
        json=payload2,
        headers={"Idempotency-Key": idempotency_key}
    )
    assert response2.status_code == 422


def test_signup_invalid_password(client):
    """Test that weak password is rejected."""
    payload = {
        "name": "Ana",
        "email": "weakpass@example.com",
        "password": "1234567890",
        "display_name": "Ana G",
    }
    
    response = client.post("/signup", json=payload)
    assert response.status_code == 422
    assert "password" in response.text.lower()


def test_get_user_success(client):
    """Test retrieving user by ID."""
    # First, create a user
    create_payload = {
        "name": "Test User",
        "email": "getuser@example.com",
        "password": "S3cure!123",
        "display_name": "Test User",
    }
    
    signup_response = client.post("/signup", json=create_payload)
    assert signup_response.status_code == 201
    user_data = signup_response.json()
    user_id = user_data["id"]
    
    # Get the user
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == user_id
    assert data["email"] == "getuser@example.com"


def test_get_user_not_found(client):
    """Test that getting non-existent user returns 404."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/users/{non_existent_id}")
    assert response.status_code == 404


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "signup-service"


def test_request_context_headers(client):
    """Test that request context headers are returned."""
    test_headers = {
        "X-Request-Id": "test-request-id",
        "X-Correlation-Id": "test-correlation-id"
    }
    
    response = client.get("/health", headers=test_headers)
    assert response.status_code == 200
    
    # Check that the response includes the context headers
    response_headers = response.headers
    assert "X-Request-Id" in response_headers
    assert "X-Correlation-Id" in response_headers
    assert response_headers["X-Request-Id"] == test_headers["X-Request-Id"]
    assert response_headers["X-Correlation-Id"] == test_headers["X-Correlation-Id"]
