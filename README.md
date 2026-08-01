# GROE Beta

**GROE — Grow Resources in Omni-sustainable Environment** turns a beginner’s available space and environmental conditions into three feasible, understandable and spatially credible edible-garden plans.

This repository is a GitHub-ready monorepo containing the React/Vite frontend, FastAPI backend, PostgreSQL schema, exactly 50 initial crop profiles, deterministic planning and spatial engines, authentication, saved plans, read-only sharing, text-only GROE Diary, weather fallback, automated tests, Docker configuration and a root-level Render Blueprint.

## What is implemented

- Anonymous planning with no more than six mandatory questions.
- English and Bahasa Indonesia interface with persisted language selection.
- Rectangle, square, L-shape and draggable custom-polygon plot input.
- Self-intersection validation and actual-polygon area/placement logic.
- Three distinct plans: Easy Start, Fast Harvest and Balanced Kitchen.
- Configurable feasibility scoring, hard constraints and user-readable adjustments.
- Quantity reduction instead of whole-plan blocking when capacity is limited.
- Deterministic, testable SVG layout coordinates with access-space reservation.
- Trellis and tiered-rack representation with deep-root tier protection.
- Exactly 50 active initial crop profiles with source and verification metadata.
- Email/password accounts, scrypt password hashing, JWT access/refresh tokens and ownership checks.
- Saved plans, account deletion and read-only public share URLs.
- Text-only diary connected to a saved plan, crop or map zone.
- Provider-independent AI seam plus deterministic diary fallback when no key exists.
- Open-Meteo geocoding and forecast integration with broad Indonesian climate fallback.
- One Dockerized service serving the compiled React app and FastAPI API from one origin.
- Alembic migrations and idempotent seeding on startup.

## Repository structure

```text
groe/
├── frontend/                 React + TypeScript + Vite
├── backend/
│   ├── app/                  FastAPI application
│   ├── migrations/           Alembic migration history
│   ├── seed_data/            Exactly 50 crop profiles
│   └── scripts/              Startup and seed scripts
├── tests/                    Backend, planning, spatial and integration tests
├── docs/                     Architecture, logic, data and deployment notes
├── Dockerfile                Multi-stage frontend/backend image
├── docker-compose.yml        Local PostgreSQL deployment
├── render.yaml               Render web service + PostgreSQL Blueprint
└── .env.example
```

## Fastest path: GitHub to Render

This repository is intentionally deployed as **one Docker web service plus one Render Postgres database**. Do not create a separate Static Site and backend service, and do not configure a frontend API URL. The compiled frontend and FastAPI API share the same origin, and the browser calls relative `/api/v1` paths.

1. Confirm that `Dockerfile`, `render.yaml`, `frontend/`, and `backend/` are visible at the **top level** of the GitHub repository. There must not be an extra `groe/` directory above them.
2. If an earlier GROE attempt already created separate frontend/backend Render services, remove those obsolete services or create this deployment under new names. A service's runtime cannot be converted in place. A workspace can also have only one active Free Postgres database.
3. In Render, choose **New → Blueprint** and connect this GitHub repository. Do not choose Static Site or configure manual build/start commands.
4. Render reads the root-level `render.yaml`, creates `groe-fullstack-beta` and `groe-fullstack-db`, generates `JWT_SECRET`, builds the Docker image, waits for Postgres, runs migrations, seeds exactly 50 profiles, and starts the app.
5. Open the generated `onrender.com` URL. `/api/v1/ready` should return `{"status":"ready"}` after deployment.

For a manual fallback deployment, create a **Docker Web Service** with repository root left blank, Dockerfile path `./Dockerfile`, Docker context `.`, and health check `/api/v1/ready`. The Blueprint route is preferred because it also wires `DATABASE_URL` correctly.

The Blueprint uses free instances for beta testing. Render Free Postgres expires after 30 days and should be upgraded before relying on it for persistent production data.

## Local Docker run

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8000`.

## Local development without Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
export DATABASE_URL=sqlite:///./groe.db   # Windows PowerShell: $env:DATABASE_URL="sqlite:///./groe.db"
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` to `http://localhost:8000`.

## Tests

```bash
pip install -r backend/requirements-dev.txt
PYTHONPATH=backend pytest -q
cd frontend && npm test
```

Backend completion result supplied with this package: **33 tests passed**. The frontend package and tests are included, but dependency installation requires access to the public npm registry.

## Database and seed operations

```bash
cd backend
alembic upgrade head
python -m scripts.seed          # idempotent; does not duplicate profiles
python -m scripts.reset_seed    # destructive reset of crop/species seed tables
```

## Environment variables

See `.env.example`. Required production values are injected by `render.yaml`. The app remains functional with `AI_PROVIDER=none` and no AI key.

## API

- OpenAPI UI: `/api/docs`
- Health: `/api/v1/health`
- Readiness: `/api/v1/ready`
- Versioned API root: `/api/v1/`

## Important beta data note

The 50 crop names and taxonomy framing follow the supplied GROE build document. Agronomic ranges in the seed are deliberately conservative beta planning values and are marked `requires_agronomist_review`. The application exposes verification metadata instead of presenting provisional values as fully authoritative.

## Known limitations

- This beta uses deterministic row/edge-aware packing rather than a computationally expensive global optimum.
- Custom polygons are editable on the frontend; backend validation remains the final authority.
- Weather is current/near-term context, not a substitute for validated long-term local agronomy data.
- The AI provider seam is present, but no commercial provider is enabled by default.
- In-memory rate limiting is suitable for one beta service instance, not a horizontally scaled production cluster.
- Crop parameter validation by an Indonesian agronomist is required before production claims.
