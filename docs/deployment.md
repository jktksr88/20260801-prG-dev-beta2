# Render Deployment — No npm Required

## What changed

Earlier builds stopped inside `npm install`. This repository removes npm from the Render production path.

The production browser files are already present in:

```text
backend/app/static/
```

FastAPI serves them directly. The Dockerfile installs only Python dependencies.

## Required GitHub root

```text
Dockerfile
render.yaml
backend/
frontend/
```

`render.yaml` and `Dockerfile` must not be inside `backend/`.

## Use the existing Blueprint

1. Upload all extracted package contents to the existing GitHub repository root.
2. Commit to `main`.
3. In Render, open the GROE web service.
4. Select **Manual Deploy → Clear build cache & deploy**.

## Leave these settings alone

The Blueprint and Dockerfile already define deployment. Do not manually enter:

- Root Directory
- Build Command
- Start Command
- Publish Directory
- frontend API URL

## Expected build pattern

You should see a Python base image and a pip dependency installation. You should not see:

```text
npm install
vite build
tsc -b
```

If npm still appears, verify that Render's deployment commit matches the newest GitHub commit and that the root Dockerfile begins with:

```dockerfile
FROM python:3.12-slim-bookworm
```

## Expected startup pattern

```text
Database is ready
Running upgrade -> 20260801_0001
Seed complete. Inserted 50 crop profiles.
Application startup complete.
Uvicorn running on http://0.0.0.0:<PORT>
```

On subsequent starts, the seed can correctly report zero inserted profiles.

## Verify deployment

Open:

```text
https://YOUR-SERVICE.onrender.com/api/v1/ready
```

Expected response:

```json
{"status":"ready"}
```

Then open the service root URL.
