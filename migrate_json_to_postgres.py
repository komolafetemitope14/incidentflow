
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from database import SessionLocal
from models import Incident


DATA_FILE = Path(__file__).resolve().parent / "incidents.json"


def parse_timestamp(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def migrate_incidents():
    if not DATA_FILE.exists():
        print(f"Migration cancelled: {DATA_FILE} does not exist.")
        return

    with DATA_FILE.open("r", encoding="utf-8") as file:
        incidents = json.load(file)

    if not isinstance(incidents, list):
        raise ValueError("Expected incidents.json to contain a list.")

    imported = 0
    skipped = 0

    with SessionLocal() as session:
        try:
            for record in incidents:
                incident_id = record["id"]

                existing = session.get(Incident, incident_id)

                if existing is not None:
                    skipped += 1
                    continue

                incident = Incident(
                    id=incident_id,
                    title=record["title"],
                    description=record["description"],
                    severity=record["severity"],
                    status=record.get("status", "Open"),
                    created_at=parse_timestamp(
                        record.get("created_at")
                    ),
                    updated_at=parse_timestamp(
                        record.get("updated_at")
                    ),
                    resolved_at=parse_timestamp(
                        record.get("resolved_at")
                    ),
                )

                session.add(incident)
                imported += 1

            session.commit()

        except Exception:
            session.rollback()
            raise

    print("JSON to PostgreSQL migration completed.")
    print(f"Imported: {imported}")
    print(f"Skipped existing records: {skipped}")


if __name__ == "__main__":
    migrate_incidents()
