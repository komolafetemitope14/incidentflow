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
