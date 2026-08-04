# GROE v8.1 validation

Release: `8.1.0`

## Automated validation

- 47 Python tests passed.
- Python bytecode compilation passed.
- JavaScript syntax validation passed for `backend/app/static/assets/app.v8.1.js`.
- Static browser application smoke test passed.
- Fresh Alembic migration passed.
- Seed inserted exactly 50 crop profiles.
- Guest diary recognized `caisimnya` as `caisim` even when the legacy payload contained Kangkung as the previously selected crop.
- English `choy sum` and Indonesian `sawi hijau` aliases passed deterministic recognition tests.
- An unnamed plant requests clarification rather than using a default crop.
- One hanging-pot module references one existing hanging-pot placement with the same placement ID and crop slug.
- Disabling vertical structures produces no hanging placement or hanging module.
- Live local API boot returned build `8.1.0`.
- A locally generated plan returned matching hanging placement/module metadata.
- A local guest-diary request for `caisimnya paling lambat tumbuhnya` returned Caisim context and did not mention Kangkung.

## Render compatibility

- Single Python Docker service architecture is unchanged.
- No npm or frontend build step was introduced.
- No new Python dependency was added.
- No database migration is required.
- `render.yaml` only advances `GROE_BUILD_VERSION` to `8.1.0`.
