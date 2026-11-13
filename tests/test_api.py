
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import api


@pytest.fixture
def client(monkeypatch):
    # Use in-memory storage so tests never modify real incidents.
    incidents = []

    def fake_load():
        return deepcopy(incidents)

    def fake_save(updated_incidents):
        incidents[:] = deepcopy(updated_incidents)

    monkeypatch.setattr(api, "load_incidents", fake_load)
    monkeypatch.setattr(api, "save_incidents", fake_save)

    return TestClient(api.app)


def create_incident(client):
    response = client.post(
        "/incidents",
        json={
            "title": "Database outage",
            "description": "PostgreSQL is unreachable",
            "severity": "Critical",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_incident(client):
    incident = create_incident(client)

    assert incident["title"] == "Database outage"
    assert incident["severity"] == "Critical"
    assert incident["status"] == "Open"
    assert incident["created_at"] is not None
    assert incident["resolved_at"] is None


def test_list_incidents(client):
    create_incident(client)

    response = client.get("/incidents")

    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_get_incident_by_id(client):
    incident = create_incident(client)

    response = client.get(f"/incidents/{incident['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == incident["id"]


def test_update_incident_status(client):
    incident = create_incident(client)

    response = client.patch(
        f"/incidents/{incident['id']}",
        json={"status": "Investigating"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Investigating"

    saved = client.get(f"/incidents/{incident['id']}")
    assert saved.json()["status"] == "Investigating"


def test_resolve_incident(client):
    incident = create_incident(client)

    response = client.patch(
        f"/incidents/{incident['id']}",
        json={"status": "Resolved"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Resolved"
    assert response.json()["resolved_at"] is not None


def test_filter_incidents(client):
    incident = create_incident(client)

    client.patch(
        f"/incidents/{incident['id']}",
        json={"status": "Resolved"},
    )

    response = client.get(
        "/incidents",
        params={
            "status": "Resolved",
            "severity": "Critical",
        },
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["incidents"][0]["id"] == incident["id"]


def test_missing_incident(client):
    response = client.get("/incidents/INC-999")

    assert response.status_code == 404


def test_invalid_severity(client):
    response = client.post(
        "/incidents",
        json={
            "title": "Invalid incident",
            "description": "Invalid severity test",
            "severity": "Extreme",
        },
    )

    assert response.status_code == 422


def test_invalid_status(client):
    incident = create_incident(client)

    response = client.patch(
        f"/incidents/{incident['id']}",
        json={"status": "Unknown"},
    )

    assert response.status_code == 422

