#!/usr/bin/env sh
set -eu

cd /app/backend

python -m scripts.wait_for_db
alembic upgrade head

case "${AUTO_SEED:-true}" in
  1|true|TRUE|yes|YES|on|ON)
    python -m scripts.seed
    # Prevent FastAPI's optional development fallback from repeating the seed.
    export AUTO_SEED=false
    ;;
esac

exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --proxy-headers \
  --forwarded-allow-ips='*'
