
# IncidentFlow

A Python-based incident management application for tracking operational incidents, managing severity and status, and supporting reliable incident response workflows.

IncidentFlow includes a command-line application and a FastAPI REST API. The REST API uses PostgreSQL for persistent incident storage, SQLAlchemy for database access, and Alembic for schema migrations.

## Project Status

**Current API version:** 1.2.0

**Automated tests:** 17 passing

**Database:** PostgreSQL 18

### Implemented Features

- Incident creation and tracking
- Incident severity classification
- Incident status updates
- Incident listing and filtering
- REST API with FastAPI
- Request validation using Pydantic
- PostgreSQL persistence for the REST API
- SQLAlchemy ORM integration
- Alembic database migrations
- JSON-to-PostgreSQL migration utility
- Incident timestamps
- Database connectivity health checks
- Automated testing with pytest
- Separate PostgreSQL test database

## Technology Stack

- Python
- FastAPI
- Pydantic
- PostgreSQL
- SQLAlchemy
- Alembic
- psycopg
- pytest
- Uvicorn
- Git and GitHub

## Architecture

The project currently supports two application interfaces.

### Command-Line Interface

The command-line application is implemented in `main.py`.

It uses a local JSON file for incident persistence.

### REST API

The REST API is implemented in `api.py`.

It uses PostgreSQL for incident persistence through SQLAlchemy.

The CLI and REST API currently use separate storage backends. Incidents created through the CLI do not automatically appear in the PostgreSQL API.

### Database Layer

`database.py` manages:

- Database configuration
- SQLAlchemy engine creation
- Database sessions
- Database dependency injection

`models.py` defines the SQLAlchemy incident model.

Alembic manages database schema changes.

## Project Structure

```text
incidentflow/
├── .gitignore
├── README.md
├── api.py
├── main.py
├── database.py
├── models.py
├── migrate_json_to_postgres.py
├── alembic.ini
├── migrations/
├── tests/
│   ├── test_api.py
│   └── test_main.py
└── .github/
```

Additional configuration and dependency files may be present depending on the development environment.

## Incident Data Model

Each incident includes the following fields:

| Field | Description |
|---|---|
| id | Unique incident identifier |
| title | Incident title |
| description | Detailed incident description |
| severity | Low, Medium, High, or Critical |
| status | Open, Investigating, Resolved, or Closed |
| created_at | Incident creation timestamp |
| updated_at | Most recent status update timestamp |
| resolved_at | Timestamp when the incident was resolved |

Incident identifiers use the format:

```text
INC-001
INC-002
INC-003
```

New incidents created through the REST API receive an identifier generated from existing database records.

## Incident Severity Levels

- Low
- Medium
- High
- Critical

## Incident Statuses

- Open
- Investigating
- Resolved
- Closed

New incidents start with the status `Open`.

When an incident is marked `Resolved`, the API records its resolution timestamp.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/komolafetemitope14/incidentflow.git
cd incidentflow
```

### 2. Create a Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the Python packages required for the API and tests:

```bash
python -m pip install fastapi uvicorn sqlalchemy psycopg[binary] pydantic-settings alembic pytest httpx
```

A dedicated dependency lock or requirements file can be added in a future milestone.

### 4. Configure PostgreSQL

Install and start PostgreSQL using the instructions for your operating system.

Create a PostgreSQL role and database with suitable permissions.

The development environment uses these database names:

```text
incidentflow
incidentflow_test
```

The test database must be separate from the main application database.

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
vi .env
```

Example configuration:

```dotenv
DATABASE_URL=postgresql+psycopg://incidentflow_user:YOUR_PASSWORD@127.0.0.1:5432/incidentflow
```

Replace the placeholder password and port with the values configured on your system.

The local development environment for this project uses PostgreSQL on port `5433`, but other installations may use `5432`.

Never commit `.env` or database credentials to GitHub.

### 6. Apply Database Migrations

```bash
python -m alembic upgrade head
```

Check the current migration:

```bash
python -m alembic current
```

The initial migration creates the `incidents` table.

### 7. Start the REST API

```bash
python -m uvicorn api:app --reload
```

The API is available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Database health check |
| GET | `/incidents` | List incidents |
| POST | `/incidents` | Create an incident |
| GET | `/incidents/{incident_id}` | Retrieve an incident |
| PATCH | `/incidents/{incident_id}` | Update incident status |

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

The health endpoint checks database connectivity and returns HTTP 503 if the database is unavailable.

### List Incidents

```bash
curl http://127.0.0.1:8000/incidents
```

### Filter Incidents by Severity

```bash
curl "http://127.0.0.1:8000/incidents?severity=Critical"
```

### Filter Incidents by Status

```bash
curl "http://127.0.0.1:8000/incidents?status=Open"
```

### Create an Incident

```bash
curl -X POST http://127.0.0.1:8000/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI training job failure",
    "description": "Training workload stopped unexpectedly",
    "severity": "Critical"
  }'
```

Successful requests return HTTP 201 and the newly created incident.

### Retrieve an Incident

```bash
curl http://127.0.0.1:8000/incidents/INC-001
```

### Update an Incident

```bash
curl -X PATCH http://127.0.0.1:8000/incidents/INC-001 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Investigating"
  }'
```

### Resolve an Incident

```bash
curl -X PATCH http://127.0.0.1:8000/incidents/INC-001 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Resolved"
  }'
```

## JSON-to-PostgreSQL Migration

The project includes `migrate_json_to_postgres.py` to import existing incidents from local JSON storage into PostgreSQL.

Run:

```bash
python migrate_json_to_postgres.py
```

The migration utility checks existing incident identifiers and skips records that have already been imported.

During the PostgreSQL integration milestone, five existing incidents were successfully migrated from JSON into PostgreSQL.

The original local JSON data is excluded from Git.

## Automated Testing

IncidentFlow uses pytest.

Run all tests:

```bash
python -m pytest -v
```

The current suite contains 17 tests:

- 10 PostgreSQL-backed REST API tests
- 7 command-line application tests

The API tests use a separate PostgreSQL database named `incidentflow_test`.

**Warning:** The API test fixture deletes records from the test database. Never point the test configuration at a database containing important information.

### API Test Coverage

The API test suite covers:

- Database health checks
- Incident creation
- Incident listing
- Incident retrieval
- Incident status updates
- Incident resolution timestamps
- Incident filtering
- Missing incidents
- Invalid severity validation
- Invalid status validation

### CLI Test Coverage

The CLI test suite covers:

- Incident ID generation
- Incident persistence
- Incident creation
- Severity validation
- Status updates
- Unknown incident handling

## Database Migrations

Alembic is used to manage schema changes.

Apply migrations:

```bash
python -m alembic upgrade head
```

Check the migration version:

```bash
python -m alembic current
```

The initial migration revision is:

```text
be0361b30eca
```

Future database schema changes should be implemented through Alembic migrations.

## Security and Data Protection

The repository excludes:

- Local database credentials
- `.env` files
- Local incident JSON files
- Backup files
- Python virtual environments
- Python cache files
- Editor swap files

The API currently focuses on incident management functionality and local development. Authentication, authorization, audit logging, and production deployment hardening are future improvements.

Do not expose the development API publicly without appropriate security controls.

## Future Improvements

- Unified PostgreSQL storage for the CLI and REST API
- API authentication and role-based authorization
- Incident ownership and assignment
- Incident activity history and audit trails
- Pagination and additional filters
- Structured application logging
- Prometheus metrics and alerting
- Containerized deployment
- Automated database migration checks in CI/CD
- Improved test database cleanup
- Kubernetes deployment and operational runbooks

## Why I Built IncidentFlow

IncidentFlow is a portfolio project focused on infrastructure reliability, incident management, and practical Python backend engineering.

It demonstrates how incident records can be created, tracked, updated, validated, stored persistently, and tested.

The project reflects real-world operational workflows involving production troubleshooting, incident ownership, and reliable service delivery.

## Author

**Komolafe Temitope Olumide**

Infrastructure and Enterprise Support Engineer

GitHub: https://github.com/komolafetemitope14

Portfolio: https://komolafetemitope14.github.io/portfolio

## License

No license has been specified for this repository.
