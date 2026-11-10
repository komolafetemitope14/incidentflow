import main


def test_generate_first_incident_id():
    incidents = []

    result = main.generate_incident_id(incidents)

    assert result == "INC-001"


def test_generate_next_incident_id():
    incidents = [
        {"id": "INC-001"},
        {"id": "INC-002"},
    ]

    result = main.generate_incident_id(incidents)

    assert result == "INC-003"


def test_save_and_load_incidents(tmp_path, monkeypatch):
    test_file = tmp_path / "test_incidents.json"

    monkeypatch.setattr(main, "DATA_FILE", test_file)

    incidents = [
        {
            "id": "INC-001",
            "title": "Database connection failure",
            "description": "Cannot connect to PostgreSQL",
            "severity": "High",
            "status": "Investigating",
        }
    ]

    assert main.save_incidents(incidents) is True

    loaded_incidents = main.load_incidents()

    assert loaded_incidents == incidents


def test_create_incident_successfully(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_FILE", tmp_path / "incidents.json")

    responses = iter([
        "API server unavailable",
        "Production API is down",
        "Critical",
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(responses)
    )

    incidents = []

    main.create_incident(incidents)

    assert len(incidents) == 1
    assert incidents[0]["id"] == "INC-001"
    assert incidents[0]["severity"] == "Critical"
    assert incidents[0]["status"] == "Open"

    assert main.load_incidents() == incidents


def test_reject_invalid_severity(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_FILE", tmp_path / "incidents.json")

    responses = iter([
        "Network outage",
        "Network connection failed",
        "Extreme",
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(responses)
    )

    incidents = []

    main.create_incident(incidents)

    assert incidents == []
    assert not main.DATA_FILE.exists()


def test_update_incident_status(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_FILE", tmp_path / "incidents.json")

    incidents = [
        {
            "id": "INC-001",
            "title": "Database failure",
            "description": "Database unavailable",
            "severity": "High",
            "status": "Open",
        }
    ]

    responses = iter(["INC-001", "2"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(responses)
    )

    main.update_incident_status(incidents)

    assert incidents[0]["status"] == "Investigating"
    assert main.load_incidents()[0]["status"] == "Investigating"


def test_reject_unknown_incident_id(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_FILE", tmp_path / "incidents.json")

    incidents = [
        {
            "id": "INC-001",
            "title": "Database failure",
            "description": "Database unavailable",
            "severity": "High",
            "status": "Open",
        }
    ]

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "INC-999"
    )

    main.update_incident_status(incidents)

    assert incidents[0]["status"] == "Open"
    assert not main.DATA_FILE.exists()
