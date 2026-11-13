
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from api import app
from database import Base, get_db, settings
from models import Incident


TEST_DATABASE_NAME = "incidentflow_test"

database_url = make_url(settings.database_url)

if database_url.database == TEST_DATABASE_NAME:
    test_database_url = database_url
else:
    test_database_url = database_url.set(
        database=TEST_DATABASE_NAME
    )

if test_database_url.database != TEST_DATABASE_NAME:
    raise RuntimeError("Refusing to test against a non-test database")

test_engine = create_engine(
    test_database_url,
    pool_pre_ping=True,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def client():
    # Ensure the test database has the expected tables.
    Base.metadata.create_all(bind=test_engine)

    # Tests are isolated from each other.
    with test_engine.begin() as connection:
        connection.execute(text("DELETE FROM incidents"))

    def override_get_db():
        with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def create_sample_incident(client):
    return client.post(
        "/incidents",
        json={
            "title": "Database outage",
            "description": "Production database unavailable",
            "severity": "Critical",
        },
    )


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_incident(client):
    response = create_sample_incident(client)

    assert response.status_code == 201

    incident = response.json()

    assert incident["id"] == "INC-001"
    assert incident["status"] == "Open"
    assert incident["severity"] == "Critical"
    assert incident["created_at"] is not None


def test_list_incidents(client):
    create_sample_incident(client)

    response = client.get("/incidents")

    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_get_incident_by_id(client):
    incident = create_sample_incident(client).json()

    response = client.get(
        f"/incidents/{incident['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == incident["id"]


def test_update_incident_status(client):
    incident = create_sample_incident(client).json()

    response = client.patch(
        f"/incidents/{incident['id']}",
        json={"status": "Investigating"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Investigating"


def test_resolve_incident(client):
    incident = create_sample_incident(client).json()

    response = client.patch(
        f"/incidents/{incident['id']}",
        json={"status": "Resolved"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Resolved"
    assert response.json()["resolved_at"] is not None


def test_filter_incidents(client):
    create_sample_incident(client)

    response = client.get(
        "/incidents?severity=Critical&status=Open"
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_missing_incident(client):
    response = client.get(
        "/incidents/INC-999"
    )

    assert response.status_code == 404


def test_invalid_severity(client):
    response = client.post(
        "/incidents",
        json={
            "title": "Invalid severity",
            "description": "Test incident",
            "severity": "Extreme",
        },
    )

    assert response.status_code == 422


def test_invalid_status(client):
    incident = create_sample_incident(client).json()

    response = client.patch(
        f"/incidents/{incident['id']}",
        json={"status": "Unknown"},
    )

    assert response.status_code == 422

