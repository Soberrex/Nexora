# Infra

No Docker is required (see `docs/decisions/0002-no-docker-neon-dev-branch.md`).

| Piece | Where | Config |
|---|---|---|
| Database | Neon (branches: `main` = production, `dev` = local development) | Neon console |
| Backend | Render Free web service, native Python | `render.yaml` (repo root = `Nexora main/`) |
| Frontend | Cloudflare Pages, built from source | Pages dashboard (settings below) |
| CI | GitHub Actions | `.github/workflows/ci.yml` |

## Branching and environments
| Branch | Purpose | Deploys to |
|---|---|---|
| `main` | Production; only receives merges from `dev` | Render (prod) + Pages production, Neon `main` branch |
| `dev` | Integration; features are merged here and tested | Pages preview URL; Neon `dev` branch |
| `feature/<name>` | One task each, branched from `dev` | CI only (Pages preview optional) |

Flow: `feature/*` -> PR into `dev` (CI must pass) -> PR `dev` into `main` (release).
Recommended GitHub settings: protect `main` and `dev` (require a pull request and passing CI; no direct pushes).

## 1. Neon
1. Create a project (Postgres 16+) and a database named `nexora`.
2. Create a `dev` branch for local development.
3. For each branch copy two connection strings: **pooled** (host contains `-pooler`) and **direct**.
4. Locally, put the `dev` URLs in `backend/.env` (`DATABASE_URL` = pooled, `MIGRATION_DATABASE_URL` = direct), then:
```bash
cd backend
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m uvicorn app.main:app --reload
curl http://localhost:8000/api/v1/health/db   # {"status":"ok","database":"connected"}
```

## 2. Render (backend)
1. Render dashboard → New → Blueprint → select the repository. Render reads `render.yaml`.
2. Enter the secrets it asks for: Neon `main` branch URLs, `CORS_ORIGINS` (your Pages URL) and `FIREBASE_PROJECT_ID`.
3. Each deploy runs `pip install . && alembic upgrade head`, then starts uvicorn. The health check is `/api/v1/health`.
4. The free plan sleeps after inactivity; the first request can take 30-60 s. The frontend shows a "waking up" state.

## 3. Cloudflare Pages (frontend)
Pages → Create → Connect to Git, then:

| Setting | Value |
|---|---|
| Root directory | `frontend` |
| Build command | `npm run build` |
| Build output directory | `dist` |
| Environment variable | `VITE_API_BASE_URL` = Render URL, e.g. `https://nexora-api.onrender.com` (no `/api/v1`) |

Node version comes from `.nvmrc`. `public/_redirects` sends every path to `index.html` so client-side routes work on refresh.

## Optional: offline Postgres
`docker compose up -d db` starts Postgres on port 5432 using `../docker-compose.yml`. An existing local Postgres works just as well.
