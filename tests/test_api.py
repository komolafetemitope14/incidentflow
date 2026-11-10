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


def test_create_incident_via_api(tmp_path, monkeypatch):
    import main

    test_file = tmp_path / "incidents.json"
    monkeypatch.setattr(main, "DATA_FILE", test_file)

    response = client.post(
        "/incidents",
        json={
            "title": "Payment gateway timeout",
            "description": "Customer payments are timing out",
            "severity": "High",
        },
    )

    assert response.status_code == 201

    created_incident = response.json()

    assert created_incident == {
        "id": "INC-001",
        "title": "Payment gateway timeout",
        "description": "Customer payments are timing out",
        "severity": "High",
        "status": "Open",
    }

    saved_incidents = main.load_incidents()

    assert len(saved_incidents) == 1
    assert saved_incidents[0] == created_incident


def test_reject_invalid_severity_via_api(tmp_path, monkeypatch):
    import main

    test_file = tmp_path / "incidents.json"
    monkeypatch.setattr(main, "DATA_FILE", test_file)

    response = client.post(
        "/incidents",
        json={
            "title": "Database outage",
            "description": "Database is unavailable",
            "severity": "Extreme",
        },
    )

    assert response.status_code == 422
    assert main.load_incidents() == []
