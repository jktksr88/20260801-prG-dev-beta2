# Completion Report — Render No-npm Revision

## Production architecture

- One Docker web service.
- One PostgreSQL database.
- Python-only production image.
- FastAPI serves both API routes and committed static browser files.
- Browser calls use relative `/api/v1` URLs.
- No production Node, npm, Vite or TypeScript build step.

The React/TypeScript/Vite source remains in `frontend/` for future development. To make the beta deployable without npm resolution, the browser application used in production is a self-contained JavaScript/CSS compatibility build in `backend/app/static/`.

## Deployment defects eliminated

- No dependency on hidden `.npmrc` files.
- No npm package-resolution step.
- No missing TypeScript configuration during Docker build.
- Startup utilities execute as Python modules.
- Startup waits for PostgreSQL before migration.
- Migration runs before seeding.
- Seed is idempotent.
- Uvicorn binds to `0.0.0.0` and Render's `$PORT`.
- Readiness endpoint checks database connectivity.

## Validation results

- Automated Python suite: **33 passed**.
- Fresh Alembic migration: passed.
- Initial database seed: **50 profiles inserted**.
- JavaScript syntax: passed.
- Isolated landing-page JavaScript render: passed.
- Live planner-to-recommendation-to-SVG flow: passed.
- Live registration-to-save-to-diary flow: passed.
- `/`, `/assets/app.js`, `/assets/styles.css`, `/api/v1/health`, `/api/v1/ready` and plant catalogue: HTTP 200.
- Recommendation endpoint returned Easy Start, Fast Harvest and Balanced Kitchen.
- Production dependency versions confirmed on public PyPI.

## Environment limitation

Docker itself is not available in the artifact-generation environment, so the final image could not be built locally here. The repository's GitHub Actions workflow performs a Docker build from the exact root Dockerfile. The Render build no longer depends on npm.
