# IncidentFlow

![Version](https://img.shields.io/badge/Version-1.3.0-blue)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-18%20Passing-brightgreen)
![CI](https://github.com/komolafetemitope14/incidentflow/actions/workflows/ci.yml/badge.svg)

## Project Overview

IncidentFlow is a Python-based incident management application designed
to support infrastructure operations, incident tracking, and service
reliability workflows.

It provides a REST API and command-line interface for creating,
classifying, tracking, and resolving operational incidents.

The application integrates persistent database storage, containerized
deployment, automated testing, continuous integration, and application
monitoring.

## System Architecture

![IncidentFlow System Architecture](docs/images/incidentflow-architecture.png)

The application uses a containerized architecture orchestrated by
Docker Compose.

- **FastAPI:** Handles incident management and REST API requests.
- **PostgreSQL:** Provides persistent incident storage.
- **Prometheus:** Collects application performance metrics.
- **Grafana:** Visualizes application health and performance.
- **GitHub Actions:** Automates testing and Docker image validation.

## Key Features

- Incident creation, tracking, and resolution.
- Severity classification and status management.
- REST API with interactive Swagger documentation.
- PostgreSQL persistence and database migrations.
- Database connectivity and application health checks.
- Docker-based service orchestration.
- Automated testing and continuous integration.
- Application monitoring and observability.
- Operational troubleshooting and recovery documentation.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Data Validation | Pydantic |
| Database | PostgreSQL 18 |
| Database ORM | SQLAlchemy |
| Database Migrations | Alembic |
| Application Server | Uvicorn |
| Containerization | Docker |
| Service Orchestration | Docker Compose |
| Automated Testing | pytest |
| Continuous Integration | GitHub Actions |
| Metrics Collection | Prometheus |
| Visualization | Grafana |
| Version Control | Git and GitHub |

## Incident Management Workflow

```mermaid
flowchart LR
    A[Incident Detected] --> B[Create Incident]
    B --> C[Classify Severity]
    C --> D[Investigating]
    D --> E[Resolved]
    E --> F[Closed]
```

### Severity Levels

| Severity | Description |
|---|---|
| Low | Minor operational issue |
| Medium | Limited service disruption |
| High | Significant operational impact |
| Critical | Major service or infrastructure failure |

### Incident Statuses

`Open` → `Investigating` → `Resolved` → `Closed`

New incidents are created with an Open status. Resolution timestamps
are recorded when incidents are marked as Resolved.

## Getting Started

### Step 1: Prerequisites

Ensure the following tools are installed:

- Git
- Docker
- Docker Compose

Verify the installation:

```bash
git --version
docker --version
docker compose version
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/komolafetemitope14/incidentflow.git
cd incidentflow
```

### Step 3: Configure Environment Variables

Set the PostgreSQL and Grafana passwords:

```bash
read -rsp "PostgreSQL password: " INCIDENTFLOW_DOCKER_DB_PASSWORD
echo
export INCIDENTFLOW_DOCKER_DB_PASSWORD

read -rsp "Grafana password: " INCIDENTFLOW_GRAFANA_ADMIN_PASSWORD
echo
export INCIDENTFLOW_GRAFANA_ADMIN_PASSWORD
```

Use strong passwords for a new installation. When using existing
Docker volumes, reuse the original credentials.

Never commit passwords or environment files to Git.

### Step 4: Deploy the Application

```bash
docker compose up -d --build
```

Docker Compose builds the application image, initializes the database,
applies database migrations, and starts the monitoring services.

### Step 5: Verify the Deployment

```bash
docker compose ps
```

The following services should be running:

- incidentflow-api-1
- incidentflow-db-1
- incidentflow-prometheus-1
- incidentflow-grafana-1

Verify API health:

```bash
curl http://127.0.0.1:8001/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

### Step 6: Access the Services

| Service | URL |
|---|---|
| FastAPI | http://127.0.0.1:8001 |
| Swagger UI | http://127.0.0.1:8001/docs |
| Health Check | http://127.0.0.1:8001/health |
| Prometheus Metrics | http://127.0.0.1:8001/metrics |
| Prometheus | http://127.0.0.1:9090 |
| Grafana | http://127.0.0.1:3001 |

## REST API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Database connectivity check |
| GET | `/metrics` | Prometheus application metrics |
| GET | `/incidents` | List incidents |
| POST | `/incidents` | Create an incident |
| GET | `/incidents/{incident_id}` | Retrieve an incident |
| PATCH | `/incidents/{incident_id}` | Update incident status |

### Create an Incident

```bash
curl -X POST http://127.0.0.1:8001/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Infrastructure service failure",
    "description": "Application service became unavailable",
    "severity": "Critical"
  }'
```

### Retrieve Incidents

```bash
curl http://127.0.0.1:8001/incidents
```

### Filter Incidents

```bash
curl "http://127.0.0.1:8001/incidents?severity=Critical"
```

### Update Incident Status

```bash
curl -X PATCH http://127.0.0.1:8001/incidents/INC-001 \
  -H "Content-Type: application/json" \
  -d '{"status": "Investigating"}'
```

Replace `INC-001` with the identifier of the incident you want to update.

## Monitoring and Observability

IncidentFlow integrates Prometheus and Grafana to provide visibility
into application health, availability, and performance.

Prometheus collects FastAPI metrics every 15 seconds, while Grafana
provides a preconfigured monitoring dashboard.

### Dashboard Metrics

| Metric | Purpose |
|---|---|
| API Availability | Monitor application scrape availability |
| HTTP Request Rate | Measure incoming application traffic |
| HTTP 5xx Error Rate | Identify server-side failures |
| Average Response Time | Monitor application performance |

Verify Prometheus connectivity using:

```promql
up{job="incidentflow-api"}
```

A result of `1` indicates that Prometheus is successfully scraping
the application.

The Grafana dashboard and Prometheus data source are automatically
provisioned during container deployment.

## Local Development

For development without Docker, install Python and configure a
PostgreSQL database.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

Create a `.env` file containing the database connection URL:

```dotenv
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@127.0.0.1:5432/incidentflow
```

Replace the username, password, and port with your PostgreSQL
configuration.

Apply database migrations and start the API:

```bash
python -m alembic upgrade head
python -m uvicorn api:app --reload
```

The local development API is available at:

http://127.0.0.1:8000/docs

The command-line application uses local JSON storage independently
of the REST API. A JSON-to-PostgreSQL migration utility is included
for importing existing incident records.

## Automated Testing

IncidentFlow uses pytest to validate application functionality.

| Test Suite | Tests Passed |
|---|---:|
| REST API | 11 |
| Command-Line Application | 7 |
| **Total** | **18** |

Test coverage includes incident creation, retrieval, filtering,
status updates, input validation, persistence, health checks,
and the metrics endpoint.

Before running tests, configure a dedicated PostgreSQL database
named `incidentflow_test` with appropriate permissions.

```bash
python -m pytest -v
```

**Warning:** API test fixtures delete records from the test database.
Never run tests against a database containing important data.

## Continuous Integration

GitHub Actions automates application validation whenever changes
are pushed or pull requests are submitted to the main branch.

```mermaid
flowchart LR
    A[Git Push] --> B[GitHub Actions]
    B --> C[Install Dependencies]
    C --> D[Run Automated Tests]
    D --> E[Build Docker Image]
    E --> F[Validation Complete]
```

The CI workflow uses an isolated PostgreSQL test database and
validates the application Docker image.

[View GitHub Actions workflows](https://github.com/komolafetemitope14/incidentflow/actions)

The pipeline performs continuous integration, not public deployment.

## Project Structure

```text
incidentflow/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── images/
│   │   └── incidentflow-architecture.png
│   └── RUNBOOK.md
├── migrations/
├── monitoring/
│   ├── prometheus/
│   └── grafana/
├── tests/
│   ├── test_api.py
│   └── test_main.py
├── api.py
├── main.py
├── database.py
├── models.py
├── migrate_json_to_postgres.py
├── alembic.ini
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Operational Management

| Operation | Command |
|---|---|
| Check service status | `docker compose ps` |
| View API logs | `docker compose logs --tail 50 api` |
| View database logs | `docker compose logs --tail 50 db` |
| Restart services | `docker compose restart` |
| Stop services | `docker compose stop` |
| Rebuild services | `docker compose up -d --build` |

PostgreSQL uses a persistent Docker volume to preserve incident
records across normal container restarts.

**Warning:** Removing Docker volumes can permanently delete
stored incident records.

For detailed troubleshooting and recovery procedures, see the
[Operational Runbook](docs/RUNBOOK.md).

## Security Considerations

- The API container runs as a non-root user.
- PostgreSQL is not directly exposed to the host network.
- Application and monitoring interfaces are bound to localhost.
- Credentials and local configuration files are excluded from Git.
- Automated tests use a dedicated database.

The current deployment is intended for local development and
demonstration. Authentication, authorization, and additional
security hardening are required before public production deployment.

## Project Validation

| Component | Last Documented Result |
|---|---|
| REST API | Passed |
| PostgreSQL Integration | Passed |
| Database Migrations | Passed |
| Docker Deployment | Passed |
| Persistent Incident Storage | Passed |
| Automated Tests | 18 Passed |
| Prometheus Metrics Collection | Verified |
| Grafana Dashboard | Verified |
| GitHub Actions Integration | Implemented |
| Operational Runbook | Completed |

## Future Improvements

- API authentication and role-based access control.
- Incident ownership and audit logging.
- Unified CLI and REST API database storage.
- Prometheus alerting and incident notifications.
- Kubernetes deployment.
- Automated database backup and recovery testing.
- Production deployment and security hardening.

## Project Version

**Current Version:** v1.3.0

[View Version Tag](https://github.com/komolafetemitope14/incidentflow/tree/v1.3.0)
