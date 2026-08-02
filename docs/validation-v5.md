# Validation — Render No-npm v5

Validated on 1 August 2026.

## Automated application tests

```text
33 passed
```

Coverage includes seed integrity, deterministic scoring, required stress scenarios, polygon and placement behavior, authentication, data ownership, saved plans, diary and integration routes.

## Database boot

- Fresh Alembic migration: passed.
- First seed: 50 crop profiles inserted.
- Second seed: 0 profiles inserted, confirming idempotency.
- Readiness endpoint: HTTP 200 with `{"status":"ready"}`.

## Browser application

- `node --check backend/app/static/assets/app.js`: passed.
- Isolated landing-page render: passed.
- Event-handler registration: passed.
- Live planner flow against FastAPI: passed.
- Three recommendation identities rendered: Easy Start, Fast Harvest and Balanced Kitchen.
- SVG layout rendered after plan selection.
- Live account registration: passed.
- Saved-plan flow: passed.
- Text diary creation and retrieval: passed.

## HTTP smoke checks

```text
/                                  200
/assets/app.js                     200
/assets/styles.css                 200
/api/v1/health                     200
/api/v1/ready                      200
/api/v1/plants?page_size=50        200
```

## Deployment-path checks

- Root `render.yaml` parsed successfully.
- Blueprint defines one Docker web service and one PostgreSQL database.
- Root Dockerfile contains no Node, npm, Vite or TypeScript build stage.
- Docker runtime command is defined by the Dockerfile.
- Browser API base is the relative path `/api/v1`.
- Production static files have no external CDN dependency.
- Production Python requirements are version-pinned.
- Each pinned production package version was confirmed to exist on public PyPI.

## Limitation

Docker is not installed in the artifact-generation environment. The included GitHub Actions workflow builds the Docker image from the exact root Dockerfile after upload.
