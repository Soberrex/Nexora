# Backend

FastAPI service exposing the REST API under `/api/v1`.

## Layout
- `app/api/v1/`: thin routers
- `app/service/`: business logic, authorization, tenant scope
- `app/repository/`: SQLAlchemy data access (always filter by `organization_id`)
- `app/domain/`: ORM models
- `app/core/`: error handling, logging
- `alembic/`: migrations

Dependency direction: route -> service -> repository -> database.

## Run locally (Python 3.12)
```bash
uv venv --python 3.12 .venv
uv pip install --python .venv -e ".[dev]"
cp ../.env.example .env      # then adjust DATABASE_URL
.venv/Scripts/python -m uvicorn app.main:app --reload   # Windows (.venv/bin on Linux/macOS)
```

## Checks
```bash
.venv/Scripts/python -m pytest
.venv/Scripts/python -m ruff check .
.venv/Scripts/python -m alembic upgrade head   # needs a reachable database
```

## Endpoints (M0)
- `GET /api/v1/health`: liveness, no DB access
- `GET /api/v1/health/db`: readiness, returns 503 when the database is unreachable
- `GET /api/v1/me`: current user (provisioned on first sign-in)
- `GET /api/v1/me/organizations`: organizations the user belongs to, with role
- `GET /api/v1/me/active-organization`: resolved active organization (`X-Organization-ID`)
- `POST /api/v1/organizations`: create an organization (super admin)
- `POST /api/v1/organizations/{id}/memberships`: add a member by email and role
- `GET|POST /api/v1/teams`: list / create teams in the active organization
- `POST /api/v1/teams/{id}/members`: add a member to a team

## CLI
```bash
.venv/Scripts/python -m app.cli make-super-admin you@example.com
```
