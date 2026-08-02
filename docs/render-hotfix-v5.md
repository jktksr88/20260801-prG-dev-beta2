# Render v5: final deployment simplification

The repeated failure point was the frontend npm build. This revision removes that entire failure class.

Render now performs only:

```text
Python image
→ pip install
→ copy backend including static website
→ wait for database
→ migrate
→ seed
→ start FastAPI
```

There is no `.npmrc`, `npm install`, Vite or TypeScript step in the production Dockerfile.
