import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from api.main import app
    return TestClient(app)


def test_healthcheck(client):
    response = client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_token_correctness(client):
    response = client.post(
        "/predictions",
        headers={"Authorization": "Bearer 00000"},
        json={
            "Brand": "Toyota",
            "model": "Innova",
            "Year": 2018,
            "kmDriven": 50000,
            "Transmission": "Manual",
            "Owner": "first",
            "FuelType": "Diesel"
        }
    )

    assert response.status_code == 200
    assert "predicted_price" in response.json()


def test_token_not_correctness(client):
    response = client.post(
        "/predictions",
        headers={"Authorization": "Bearer 12345"},
        json={
            "Brand": "Toyota",
            "model": "Innova",
            "Year": 2018,
            "kmDriven": 50000,
            "Transmission": "Manual",
            "Owner": "first",
            "FuelType": "Diesel"
        }
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid authentication credentials"
    }


def test_token_absent(client):
    response = client.post(
        "/predictions",
        json={
            "Brand": "Toyota",
            "model": "Innova",
            "Year": 2018,
            "kmDriven": 50000,
            "Transmission": "Manual",
            "Owner": "first",
            "FuelType": "Diesel"
        }
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_inference(client):
    response = client.post(
        "/predictions",
        headers={"Authorization": "Bearer 00000"},
        json={
            "Brand": "Toyota",
            "model": "Innova",
            "Year": 2018,
            "kmDriven": 50000,
            "Transmission": "Manual",
            "Owner": "first",
            "FuelType": "Diesel"
        }
    )

    assert response.status_code == 200
    assert response.json()["predicted_price"] > 0