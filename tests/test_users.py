import pytest
from app import create_app
from app.database import db

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client


def test_create_user(client):
    response = client.post(
        "/api/users/",
        json={"email": "test@example.com", "password": "password123", "name": "Test User"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"


def test_get_users(client):
    # Crear un usuario primero
    client.post(
        "/api/users/",
        json={"email": "test2@example.com", "password": "password123", "name": "Test User 2"},
    )
    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.get_json()
    assert any(u["email"] == "test2@example.com" for u in data) 