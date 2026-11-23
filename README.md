
# IncidentFlow

A Python-based incident management application for tracking operational incidents, managing severity and status, and supporting reliable incident response workflows.

IncidentFlow includes a command-line application and a FastAPI REST API. The REST API uses PostgreSQL for persistent incident storage, SQLAlchemy for database access, and Alembic for schema migrations.

The application also supports local containerized deployment using Docker and Docker Compose.

## Project Status

**Current API version:** 1.2.0

**Automated tests:** 17 passing (last documented test run)

**Database:** PostgreSQL 18

**Docker deployment:** Successfully tested locally

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
- Dockerized FastAPI application
- PostgreSQL container with persistent storage
- Docker Compose service orchestration
- Database health checks and startup dependencies
- Automatic database migrations during container startup
- Verified incident persistence across container restarts

## Technology Stack

- Python
- FastAPI
- Pydantic
- PostgreSQL 18
- SQLAlchemy
- Alembic
- psycopg
- pytest
- Uvicorn
- Docker
- Docker Compose
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

### Docker Architecture

The Docker Compose environment contains two services:

**API service**

- Runs the FastAPI application
- Uses a Python 3.14 slim base image
- Runs as a non-root user
- Exposes the application on `127.0.0.1:8001`
- Applies Alembic migrations during startup

**Database service**

- Runs PostgreSQL 18
- Uses a persistent Docker volume
- Includes a database readiness health check
- Communicates with the API over the Docker Compose network
- Does not publish its database port to the host

The API waits for the PostgreSQL health check to succeed before starting.

## Project Structure

```text
incidentflow/
├── .dockerignore
├── .gitignore
├── README.md
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── requirements-dev.txt
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

Local configuration files, incident data, backups, and virtual environments are excluded from Git where appropriate.

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

There are two ways to run IncidentFlow:

1. Local Python development with PostgreSQL
2. Docker Compose

For a containerized setup, follow the Docker Compose instructions below.

### 1. Clone the Repository

```bash
git clone https://github.com/komolafetemitope14/incidentflow.git
cd incidentflow
```

### 2. Create a Python Virtual Environment

For local Python development:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the application dependencies:

```bash
python -m pip install -r requirements.txt
```

For automated testing, also install:

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Configure PostgreSQL

Install and start PostgreSQL using the instructions for your operating system.

Create a PostgreSQL role and database with suitable permissions.

The local development environment uses these database names:

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

The existing local development environment has used PostgreSQL on port `5433`, but other installations may use `5432`.

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

The locally started API is available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Running IncidentFlow with Docker Compose

IncidentFlow supports containerized local development using Docker Compose.

The Docker environment runs FastAPI and PostgreSQL in separate containers.

### Prerequisites

- Docker Engine or Docker Desktop
- Docker Compose

Verify installation:

```bash
docker --version
docker compose version
```

### Configure the Database Password

Set a strong password for the Docker PostgreSQL database:

```bash
export INCIDENTFLOW_DOCKER_DB_PASSWORD='REPLACE_WITH_YOUR_SECURE_PASSWORD'
```

Replace the placeholder with a secure password.

For an existing PostgreSQL database volume, reuse the original database password. Changing the environment variable does not automatically change the password stored in an initialized PostgreSQL database.

Do not commit credentials to Git.

The environment variable must be available whenever Docker Compose processes this configuration.

### Start the Application

```bash
docker compose up -d --build
```

Docker Compose:

1. Builds the FastAPI application image.
2. Starts the PostgreSQL container.
3. Waits for PostgreSQL to become healthy.
4. Starts the FastAPI container.
5. Applies Alembic database migrations.
6. Starts the Uvicorn application server.

### Verify Container Status

```bash
docker compose ps
```

Expected services:

```text
incidentflow-api-1
incidentflow-db-1
```

The database should report a healthy status.

### Test the API

Run:

```bash
curl http://127.0.0.1:8001/health
```

Expected response:

```json
{"status":"healthy"}
```

Retrieve incidents:

```bash
curl http://127.0.0.1:8001/incidents
```

Interactive API documentation:

```text
http://127.0.0.1:8001/docs
```

### Persistent Database Storage

PostgreSQL uses a named Docker volume to preserve incident records across normal container restarts.

The Compose configuration defines:

```yaml
volumes:
  postgres_data:
```

For the default project name, the Docker volume is named:

```text
incidentflow_postgres_data
```

The PostgreSQL 18 container mounts this volume at:

```text
/var/lib/postgresql
```

### Verified Docker Persistence Test

The Docker environment was successfully tested on November 23, 2026.

The test involved:

1. Starting the FastAPI and PostgreSQL containers.
2. Confirming PostgreSQL was healthy.
3. Confirming the API health endpoint returned HTTP 200.
4. Creating a simulated Critical incident.
5. Retrieving the incident through the REST API.
6. Restarting both containers.
7. Retrieving the same incident after the restart.

The test incident was:

```text
ID: INC-001
Title: AI training workload failure
Severity: Critical
Status: Open
```

The incident remained available after both containers restarted.

This confirms data persistence across normal container restarts. It does not replace database backups or disaster recovery testing.

### Restart Containers

```bash
docker compose restart
```

### Stop Containers

```bash
docker compose stop
```

This stops the services without deleting the containers or persistent database volume.

### View Logs

```bash
docker compose logs --tail 50 api
```

Database logs:

```bash
docker compose logs --tail 50 db
```

### Important Data Protection Warning

Avoid running:

```bash
docker compose down -v
```

unless you intentionally want to remove the project's database volume and its stored data.

Removing the database volume can permanently delete locally stored incident records.

### Docker Security Notes

- The API is bound to `127.0.0.1:8001` for local development.
- PostgreSQL is not published directly to the host.
- The API container runs as a non-root user.
- Local secrets and backups are excluded from the Docker build context.
- Database credentials must not be committed to Git.
- Authentication, authorization, and production security hardening remain future improvements.

The current Docker environment is intended for local development and demonstration, not unrestricted public deployment.

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Database health check |
| GET | `/incidents` | List incidents |
| POST | `/incidents` | Create an incident |
| GET | `/incidents/{incident_id}` | Retrieve an incident |
| PATCH | `/incidents/{incident_id}` | Update incident status |

The examples below use the local Python development port `8000`.

When using Docker Compose, replace port `8000` with `8001`.

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

During the original PostgreSQL integration milestone, five existing incidents were successfully migrated from JSON into PostgreSQL.

The original local JSON data is excluded from Git.

The Docker database is separate from the original local PostgreSQL database. Existing local records are not automatically imported into the Docker database.

## Automated Testing

IncidentFlow uses pytest.

Run all tests:

```bash
python -m pytest -v
```

The last documented test suite contained 17 passing tests:

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

Alembic is used to manage database schema changes.

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

In the Docker Compose environment, Alembic migrations run automatically when the API container starts.

## Security and Data Protection

The repository excludes:

- Local database credentials
- `.env` files
- Local incident JSON files
- Backup files
- Python virtual environments
- Python cache files
- Editor swap files

The Docker build context also excludes local data, secrets, backups, and unnecessary development files.

The API currently focuses on incident management functionality and local development.

Authentication, authorization, audit logging, and production deployment hardening are future improvements.

Do not expose the development API publicly without appropriate security controls.

## Future Improvements

- Unified PostgreSQL storage for the CLI and REST API
- API authentication and role-based authorization
- Incident ownership and assignment
- Incident activity history and audit trails
- Pagination and additional filters
- Structured application logging
- Prometheus metrics and alerting
- Production container deployment and hardening
- Automated database migration checks in CI/CD
- Improved test database cleanup
- Kubernetes deployment and operational runbooks
- Automated database backup and recovery testing

## Why I Built IncidentFlow

IncidentFlow is a portfolio project focused on infrastructure reliability, incident management, and practical Python backend engineering.

It demonstrates how incident records can be created, tracked, updated, validated, stored persistently, and tested.

The project also demonstrates containerized service deployment, PostgreSQL integration, database migrations, application health checks, and persistence verification.

It reflects real-world operational workflows involving production troubleshooting, incident ownership, and reliable service delivery.

## Author

**Komolafe Temitope Olumide**

Infrastructure and Enterprise Support Engineer

GitHub: https://github.com/komolafetemitope14

Portfolio: https://komolafetemitope14.github.io/portfolio

## License

No license has been specified for this repository.
