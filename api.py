
from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from main import (
    generate_incident_id,
    load_incidents,
    save_incidents,
)


app = FastAPI(
    title="IncidentFlow API",
    description="Enterprise Incident Management REST API",
    version="1.1.0",
)


Severity = Literal["Low", "Medium", "High", "Critical"]
Status = Literal["Open", "Investigating", "Resolved", "Closed"]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    severity: Severity


class IncidentUpdate(BaseModel):
    status: Status


@app.get("/")
def home():
    return {
        "application": "IncidentFlow",
        "message": "IncidentFlow API is running",
        "version": "1.1.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/incidents")
def get_incidents(
    status: Optional[Status] = None,
    severity: Optional[Severity] = None,
):
    incidents = load_incidents()

    if status is not None:
        incidents = [
            incident for incident in incidents
            if incident.get("status") == status
        ]

    if severity is not None:
        incidents = [
            incident for incident in incidents
            if incident.get("severity") == severity
        ]

    return {
        "count": len(incidents),
        "incidents": incidents,
    }


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    incidents = load_incidents()

    for incident in incidents:
        if str(incident["id"]) == incident_id:
            return incident

    raise HTTPException(
        status_code=404,
        detail="Incident not found",
    )


@app.post("/incidents", status_code=201)
def create_incident(incident: IncidentCreate):
    incidents = load_incidents()
    timestamp = utc_now()

    new_incident = {
        "id": generate_incident_id(incidents),
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": "Open",
        "created_at": timestamp,
        "updated_at": timestamp,
        "resolved_at": None,
    }

    incidents.append(new_incident)
    save_incidents(incidents)

    return new_incident


@app.patch("/incidents/{incident_id}")
def update_incident(
    incident_id: str,
    update: IncidentUpdate,
):
    incidents = load_incidents()

    for incident in incidents:
        if str(incident["id"]) == incident_id:
            previous_status = incident.get("status")

            incident["status"] = update.status
            incident["updated_at"] = utc_now()

            if update.status == "Resolved":
                if previous_status != "Resolved":
                    incident["resolved_at"] = utc_now()
            else:
                incident["resolved_at"] = None

            save_incidents(incidents)
            return incident

    raise HTTPException(
        status_code=404,
        detail="Incident not found",
    )

