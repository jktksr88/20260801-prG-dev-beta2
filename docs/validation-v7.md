# GROE v7 Validation Report

Release: `7.0.0`

## Automated validation

- `41 passed` in the complete Python test suite.
- JavaScript syntax validation passed for `backend/app/static/assets/app.v7.js`.
- Static browser landing-page smoke test passed.
- Python byte-code compilation passed for the application, migration and startup modules.
- `render.yaml` parses correctly and declares one Docker service, one PostgreSQL database and build version `7.0.0`.

## Clean-runtime validation

A fresh temporary database was used to validate the same runtime sequence used by Render:

1. Alembic upgraded an empty database to revision `20260801_0001`.
2. First seed inserted exactly 50 crop profiles.
3. Second seed inserted zero crop profiles.
4. Uvicorn started successfully.
5. `/`, `/api/v1/build`, `/api/v1/health`, `/api/v1/ready`, `/assets/app.v7.js` and `/assets/styles.v7.css` returned HTTP 200.
6. Each response returned `X-GROE-Build: 7.0.0`.
7. HTML/API responses used `Cache-Control: no-store`; versioned assets used immutable caching.
8. Indonesian location search returned a curated Jakarta result even without relying on the external geocoder.
9. A mixed-surface planner request returned three plans with both soil and container placements.
10. At least one crop included a calculated container recommendation.

## Client-feedback coverage

- Location dropdown: tested.
- Open-Meteo request mapping and weather fallback: tested.
- Stable crop visual mapping and complete map legend: source and integration tested.
- Pot recommendations included in layout footprints: planning and integration tested.
- Cards below map with guide modal: source and integration tested.
- Public 50-crop catalogue removed from deployed frontend: source tested.
- Guest diary without sign-in: API and integration tested.
- Optional AI provider with deterministic fallback: integration tested.
- Distinct build endpoint and v7 assets: integration tested.

## External live limitation

The validation environment could not resolve the public Render hostname, so it could not independently fetch the user's live service. The `/api/v1/build` endpoint, response header and unique asset names were added specifically to make the deployed version objectively verifiable after the user uploads the release.
