# GROE v8.2 validation report

Release: `8.2.0`

## Automated validation

- 54 Python tests passed.
- JavaScript syntax validation passed for `app.v8.2.js`.
- Static browser application smoke test passed.
- Fresh Alembic migration passed.
- First seed inserted exactly 50 crop profiles.
- Second seed inserted zero duplicate profiles.

## Regression coverage

- `pokcoy` resolves to Pakcoy.
- `caisin` resolves to Caisim / sawi hijau.
- `bok choy` and `choy sum` resolve in English.
- A note naming Pakcoy and Caisim returns both crops without clarification.
- Multi-crop deterministic guidance addresses each crop separately and never mentions Kangkung unless Kangkung is named.
- Rack assignments reference real placement IDs and matching tier numbers.
- Caisim is not silently assigned to a hanging pot.
- Hanging-pot quantity remains part of the original calculated quantity.
- Static UI includes external sunlight direction, N/E/S/W compass, explicit rack/hanging assignments, and multi-crop badges.

## Render compatibility

- No npm, Node, TypeScript, or Vite build is used by Render.
- Dockerfile, startup command, migrations, seed process, health check, and database configuration are unchanged.
- `render.yaml` only advances `GROE_BUILD_VERSION` to `8.2.0`.
- No new environment variable is required.
