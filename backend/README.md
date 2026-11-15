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
