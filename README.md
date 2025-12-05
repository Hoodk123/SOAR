# SOAR Platform Backend

## Context
This is the backend for a Security Orchestration Automation and Response (SOAR) platform. It provides a RESTful API for managing security alerts, incidents, and automated playbooks.

## Tech Stack
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy (ORM)
- **Authentication**: (To be confirmed/implemented)
- **API Style**: REST

## API Endpoints

### Alerts (`/api/v1/alerts`)
- `GET /`: List all alerts (supports filtering by severity, status, source).
- `POST /`: Create a new alert.
- `GET /<id>`: Get alert details.
- `PUT /<id>`: Update alert details.
- `DELETE /<id>`: Delete an alert.
- `GET /statistics`: Get alert statistics (counts by severity/status).
- `GET /search`: Search alerts.
- `POST /<id>/escalate`: Escalate an alert.
- `GET /<id>/timeline`: Get alert history.
- `POST /bulk-update`: Update multiple alerts at once.
- `GET /sources`: Get alerts count by source.

## Running the Backend
1.  Create a virtual environment: `python -m venv venv`
2.  Activate it: `source venv/bin/activate`
3.  Install dependencies: `pip install -r requirements.txt`
4.  Run the server: `python run.py`
