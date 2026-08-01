# GROE Render deployment audit

## Critical defects corrected

1. The Docker frontend stage did not copy `frontend/tsconfig.app.json`, although `tsc -b` requires it. The image build therefore stopped before Vite could compile the frontend.
2. The startup command attempted Alembic immediately. A newly provisioned Render Postgres database can still be starting, so one transient connection failure could terminate the first deploy. A bounded database readiness retry now runs first.
3. Startup seeded twice: once in `start.sh` and again in the FastAPI lifespan hook. The startup script now disables the fallback after completing the idempotent seed.
4. The Blueprint used deprecated `autoDeploy`. It now uses `autoDeployTrigger` and explicitly defines the Docker build context.
5. The Render health check only confirmed that the HTTP process existed. It now uses the readiness endpoint that also verifies database connectivity.
6. Generated Vite/TypeScript files were committed and could become stale. They are removed and ignored.
7. The startup script executed files directly from `backend/scripts/`, which made Python search that directory instead of the backend root and caused `ModuleNotFoundError: app`. Startup utilities now run with `python -m scripts...`.
8. Test-only packages and Uvicorn optional compiled extras were installed in the production image. Production and development requirements are now separated.
9. GitHub Actions attempted npm dependency caching without a lockfile. The invalid cache configuration is removed until a real `package-lock.json` is generated and committed.

## Architecture retained intentionally

- One Dockerized Render web service serves both compiled React assets and FastAPI.
- Browser API calls remain relative to `/api/v1`; no `VITE_API_URL` or `import.meta.env` setting is required.
- `DATABASE_URL` is injected from the Render Postgres internal connection string.
- The service binds to `0.0.0.0` and Render's `PORT` value.

## Remaining recommendation

Generate and commit `frontend/package-lock.json` from a normal machine with access to the public npm registry, then change Docker and CI installs from `npm install` to `npm ci`. The current files deliberately use `npm install` so the repository does not fail merely because a lockfile is absent.
