# Architecture

## System boundary

GROE deploys as one Dockerized Render web service and one Render PostgreSQL database. The production browser application is committed under `backend/app/static`; FastAPI serves both the website and `/api/v1` from one origin.

The original React/TypeScript/Vite source remains under `frontend/` for future development, but it is deliberately excluded from the Render build. This removes Node and npm as production deployment dependencies.

## Runtime layers

1. **Browser presentation layer** — guided planner, plan comparison, SVG result map, saved gardens, sharing and diary.
2. **FastAPI application layer** — typed API schemas, validation, authentication, ownership and request logging.
3. **Deterministic planning layer** — normalization, climate context, crop scoring, hard constraints, combination ranking and diversity.
4. **Spatial layer** — Shapely polygon validation, usable-area calculation, access-zone reservation and deterministic packing.
5. **Persistence layer** — SQLAlchemy models, Alembic migrations and PostgreSQL.
6. **External context layer** — Open-Meteo geocoding/forecast with controlled fallback.
7. **Explanation layer** — deterministic plan copy and diary guidance, with a provider-independent AI interface.

## Principal data flow

```text
Planner form
  → Pydantic validation
  → polygon normalization
  → weather + broad climate context
  → score all 50 profiles
  → enforce physical hard constraints
  → rank three different objective functions
  → calculate target quantities
  → pack placements inside actual usable polygon
  → reduce quantities that do not fit
  → return plan comparison + SVG coordinates + reason codes
```

## Security model

- Passwords use salted `hashlib.scrypt` hashes.
- Access and refresh JWTs have separate token types and expiry periods.
- Refresh tokens are stored only as SHA-256 digests and can be revoked.
- Private plan and diary routes enforce user ownership.
- Public plan routes expose only intended read-only plan fields.
- Diary text is normalized, control characters removed and HTML escaped.
- Authentication and diary/AI routes use a sliding-window beta rate limiter.
- Secrets are environment variables and are never committed.
- Responses include request IDs and avoid exposing stack traces.

## Static serving

FastAPI mounts `/assets` from `backend/app/static/assets` and returns `index.html` for non-API routes. This supports direct browser navigation to public share URLs such as `/shared/{share_slug}` without a separate static-site service.
