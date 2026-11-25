# IncidentFlow Operational Runbook

## Overview

IncidentFlow runs four Docker services:
FastAPI, PostgreSQL, Prometheus, and Grafana.

## Service URLs

- API: http://127.0.0.1:8001
- API health: http://127.0.0.1:8001/health
- API metrics: http://127.0.0.1:8001/metrics
- Prometheus: http://127.0.0.1:9090
- Grafana: http://127.0.0.1:3001

## Check Application Health

Run:

    curl -fsS http://127.0.0.1:8001/health

Expected response:

    {"status":"healthy"}

## Check Prometheus

Open http://127.0.0.1:9090 and run:

    up{job="incidentflow-api"}

A result of 1 indicates successful scraping.

## Check Grafana

Open http://127.0.0.1:3001

Navigate to:
Dashboards > IncidentFlow > IncidentFlow Monitoring Overview

## Docker Operations

Before running Docker Compose, ensure both
INCIDENTFLOW_DOCKER_DB_PASSWORD and
INCIDENTFLOW_GRAFANA_ADMIN_PASSWORD are set.

Check containers:

    docker compose ps

View API logs:

    docker compose logs --tail=50 api

View database logs:

    docker compose logs --tail=50 db

View monitoring logs:

    docker compose logs --tail=50 prometheus
    docker compose logs --tail=50 grafana

Restart API:

    docker compose restart api

Stop services safely:

    docker compose stop

## Troubleshooting

If the API fails, inspect API and database logs.

If Prometheus reports the API as down,
verify that /metrics is accessible.

If Grafana displays No data, check the
Prometheus data source and dashboard time range.

If a port is occupied, identify the conflicting
process before changing the Compose configuration.

## Data Protection

PostgreSQL uses persistent Docker storage.

Never run docker compose down -v unless you
intentionally want to delete persistent volumes.

Do not run API tests against production or
important incident data.

Use a separate PostgreSQL test database.

## Security

This deployment is intended for local development.

Do not publicly expose the services without
authentication and additional security controls.
