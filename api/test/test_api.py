from fastapi.testclient import TestClient


def test_healthcheck():
    from api.main import app

    client = TestClient(app)

    response = client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}