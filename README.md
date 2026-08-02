# GROE Beta — Render-Safe Single Runtime

**GROE — Grow Resources in Omni-sustainable Environment** turns a beginner's available space and conditions into three feasible edible-garden plans.

This revision is designed to remove the deployment failure that repeatedly blocked Render: **Render does not run Node, npm, TypeScript or Vite at all.**

Production uses:

- one Docker web service;
- one Render PostgreSQL database;
- one Python runtime;
- FastAPI for the API;
- a self-contained browser application committed under `backend/app/static/`;
- relative `/api/v1` requests, so frontend and backend share one origin.

The original React + TypeScript + Vite development source remains in `frontend/` for future development. Render does not build that directory. The production-compatible browser bundle is plain JavaScript and CSS so npm package resolution cannot stop deployment.

## Render deployment

At the GitHub repository root, confirm that these items are immediately visible:

```text
Dockerfile
render.yaml
backend/
frontend/
```

Then:

1. Upload this package's contents to the repository root and commit to `main`.
2. Open the existing Render web service.
3. Choose **Manual Deploy → Clear build cache & deploy**.
4. Do not enter a Root Directory, Build Command, Start Command, Publish Directory or frontend API URL.

A successful build contains no `npm install`, `vite build` or `tsc` command. If the Render log still shows npm, Render is building an older commit or older Dockerfile.

After deployment, open:

```text
https://YOUR-SERVICE.onrender.com/api/v1/ready
```

Expected response:

```json
{"status":"ready"}
```

Then open the service root URL for the GROE interface.

## Runtime boot order

The container:

1. waits for PostgreSQL;
2. runs Alembic migrations;
3. inserts the 50 crop profiles when absent;
4. starts Uvicorn on Render's `$PORT`;
5. serves both the website and `/api/v1` from the same origin.

## Implemented beta functions

- English and Indonesian interface.
- Anonymous planner journey.
- Exactly 50 initial crop profiles.
- Three deterministic recommendation plans.
- Feasibility scores, hard constraints and adjustment reasons.
- Quantity reduction when plot capacity is limited.
- Polygon-aware spatial placement and scaled SVG result map.
- Trellis and vertical-tier rules.
- Email/password authentication and JWT access/refresh tokens.
- Saved plans and public read-only sharing.
- Text-only GROE Diary with deterministic fallback.
- Open-Meteo integration with graceful fallback.
- PostgreSQL schema, Alembic migration and idempotent seed.

## Repository structure

```text
├── backend/
│   ├── app/
│   │   ├── static/             Production browser application served by FastAPI
│   │   ├── api/
│   │   ├── planning/
│   │   ├── spatial/
│   │   └── main.py
│   ├── migrations/
│   ├── seed_data/
│   ├── scripts/
│   └── requirements.txt
├── frontend/                   Original React/TypeScript/Vite development source
├── tests/
├── docs/
├── Dockerfile                  Python-only production image
├── render.yaml
└── docker-compose.yml
```

## Local Docker run

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8000`.

## Local non-Docker run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
export DATABASE_URL=sqlite:///./groe.db
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload --port 8000
```

## Validation completed for this package

- 33 automated backend, planning, spatial, authentication and integration tests passed.
- Fresh Alembic migration completed.
- Initial seed inserted exactly 50 profiles.
- JavaScript syntax check passed.
- Browser-code landing-page render passed in an isolated JavaScript runtime.
- Live planner flow reached the API, returned three plans and rendered the SVG plan.
- Live account registration, plan save and diary entry flow passed.
- Root website, JavaScript, CSS, health, readiness and plant endpoints returned HTTP 200.
- Every pinned production Python package version was confirmed to exist on public PyPI.
- Dockerfile contains no Node or npm stage.

## Important data note

The crop data is appropriate for beta logic validation. Provisional agronomic ranges remain labelled for agronomist review before production claims.
