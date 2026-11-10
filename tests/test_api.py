from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_api_home():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "application": "IncidentFlow",
        "message": "IncidentFlow API is running",
        "version": "1.0.0",
    }


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
    }
