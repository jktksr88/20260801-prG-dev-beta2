# Deployment

## Required Render architecture

Deploy GROE as one Docker web service and one Render Postgres database. The React production build is copied into FastAPI's static directory, so the website and `/api/v1` share one origin. Do not create a separate Render Static Site and do not add a frontend API URL.

## Blueprint path

Keep these entries at the GitHub repository root:

- `render.yaml`
- `Dockerfile`
- `frontend/`
- `backend/`

Then choose **New → Blueprint** in Render. Leave manual Root Directory, Build Command, Start Command, and Publish Directory settings unused; the Blueprint and Dockerfile define them.

`render.yaml` creates:

- Docker web service `groe-fullstack-beta`
- Render Postgres database `groe-fullstack-db`
- Singapore-region resources
- automatic internal `DATABASE_URL` injection
- generated `JWT_SECRET`
- database-backed readiness check at `/api/v1/ready`
- keyless Open-Meteo configuration

## Container boot order

The Docker `CMD` executes `backend/scripts/start.sh`, which:

1. waits for the database with bounded retries;
2. runs `alembic upgrade head`;
3. runs the idempotent seed as `python -m scripts.seed`;
4. starts Uvicorn on Render's `$PORT`, bound to `0.0.0.0`.

## Existing failed Render attempts

Do not reuse a separately created frontend Static Site or a native Python web service for this package. Create a fresh Blueprint deployment or remove obsolete GROE resources first. Render service runtimes and regions cannot be changed after creation, and a workspace can have only one active Free Postgres database.

## Manual Docker fallback

When Blueprint creation is unavailable, create one **Docker Web Service** with:

- Root Directory: blank
- Dockerfile Path: `./Dockerfile`
- Docker Context: `.`
- Health Check Path: `/api/v1/ready`

Create Postgres separately and set `DATABASE_URL` to its internal connection string. Also set a long random `JWT_SECRET`.

## Free database warning

Render Free Postgres is for beta testing and expires after 30 days. Upgrade before relying on saved plans, accounts, or diary entries as persistent user data.

## Production upgrade checklist

- Generate and commit `frontend/package-lock.json`, then use `npm ci` in Docker and CI.
- Upgrade Postgres to a paid plan with backups.
- Add centralized rate limiting before scaling beyond one web instance.
- Review provisional agronomy fields with an Indonesian agronomist.
- Add external uptime and error monitoring.
