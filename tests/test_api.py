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


def test_get_incidents(tmp_path, monkeypatch):
    import main

    test_file = tmp_path / "incidents.json"

    monkeypatch.setattr(main, "DATA_FILE", test_file)

    incidents = [
        {
            "id": "INC-001",
            "title": "Database failure",
            "description": "Database unavailable",
            "severity": "High",
            "status": "Investigating",
        }
    ]

    main.save_incidents(incidents)

    response = client.get("/incidents")

    assert response.status_code == 200
    assert response.json() == {
        "count": 1,
        "incidents": incidents,
    }
