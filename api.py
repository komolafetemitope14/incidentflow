from typing import Literal

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
    version="1.0.0",
)


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    severity: Literal["Low", "Medium", "High", "Critical"]


@app.get("/")
def home():
    return {
        "application": "IncidentFlow",
        "message": "IncidentFlow API is running",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


@app.get("/incidents")
def get_incidents():
    incidents = load_incidents()

    return {
        "count": len(incidents),
        "incidents": incidents,
    }


@app.post("/incidents", status_code=201)
def create_incident(incident: IncidentCreate):
    incidents = load_incidents()

    new_incident = {
        "id": generate_incident_id(incidents),
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": "Open",
    }

    incidents.append(new_incident)
    save_incidents(incidents)

    return new_incident
