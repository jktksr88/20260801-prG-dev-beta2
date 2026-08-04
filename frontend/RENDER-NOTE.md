# Archived development frontend

This React/TypeScript/Vite directory is retained only as a development reference. It is **not** copied into the Render Docker build.

The live Render application is the tested, versioned browser bundle under:

```text
backend/app/static/
```

Do not add a separate Render Static Site or frontend service. The FastAPI service serves both the website and `/api/v1` from one origin.
