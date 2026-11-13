
from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from database import get_db
from models import Incident


app = FastAPI(
    title="IncidentFlow API",
    description="Enterprise Incident Management REST API",
    version="1.2.0",
)


Severity = Literal["Low", "Medium", "High", "Critical"]
Status = Literal["Open", "Investigating", "Resolved", "Closed"]


def utc_now():
    return datetime.now(timezone.utc)


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    severity: Severity


class IncidentUpdate(BaseModel):
    status: Status


def incident_to_dict(incident: Incident):
    def timestamp(value):
        if value is None:
            return None

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.isoformat()

    return {
        "id": incident.id,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status,
        "created_at": timestamp(incident.created_at),
        "updated_at": timestamp(incident.updated_at),
        "resolved_at": timestamp(incident.resolved_at),
    }


def generate_incident_id(db: Session):
    # Serialize ID allocation across concurrent requests.
    # This advisory lock is scoped to the current transaction.
    db.execute(
        text("SELECT pg_advisory_xact_lock(73421, 1)")
    )

    existing_ids = db.scalars(
        select(Incident.id)
    ).all()

    existing_numbers = []

    for incident_id in existing_ids:
        if incident_id.startswith("INC-"):
            try:
                number = int(incident_id.split("-")[1])
                existing_numbers.append(number)
            except (ValueError, IndexError):
                continue

    next_number = max(existing_numbers, default=0) + 1

    return f"INC-{next_number:03d}"


@app.get("/")
def home():
    return {
        "application": "IncidentFlow",
        "message": "IncidentFlow API is running",
        "version": "1.2.0",
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )

    return {"status": "healthy"}


@app.get("/incidents")
def get_incidents(
    status: Optional[Status] = None,
    severity: Optional[Severity] = None,
    db: Session = Depends(get_db),
):
    statement = select(Incident).order_by(Incident.id)

    if status is not None:
        statement = statement.where(
            Incident.status == status
        )

    if severity is not None:
        statement = statement.where(
            Incident.severity == severity
        )

    incidents = db.scalars(statement).all()

    return {
        "count": len(incidents),
        "incidents": [
            incident_to_dict(incident)
            for incident in incidents
        ],
    }


@app.get("/incidents/{incident_id}")
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident_to_dict(incident)


@app.post("/incidents", status_code=201)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
):
    try:
        incident_id = generate_incident_id(db)
        timestamp = utc_now()

        new_incident = Incident(
            id=incident_id,
            title=incident.title,
            description=incident.description,
            severity=incident.severity,
            status="Open",
            created_at=timestamp,
            updated_at=timestamp,
            resolved_at=None,
        )

        db.add(new_incident)
        db.commit()
        db.refresh(new_incident)

        return incident_to_dict(new_incident)

    except Exception:
        db.rollback()
        raise


@app.patch("/incidents/{incident_id}")
def update_incident(
    incident_id: str,
    update: IncidentUpdate,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    previous_status = incident.status

    incident.status = update.status
    incident.updated_at = utc_now()

    if update.status == "Resolved":
        if previous_status != "Resolved":
            incident.resolved_at = utc_now()
    else:
        incident.resolved_at = None

    try:
        db.commit()
        db.refresh(incident)

        return incident_to_dict(incident)

    except Exception:
        db.rollback()
        raise

