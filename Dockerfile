# GROE single-runtime production image.
# The browser frontend is committed under backend/app/static, so Render does
# not need Node, npm, TypeScript, Vite, or a frontend build step.
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install production dependencies before copying the application for caching.
COPY backend/requirements.txt /app/backend/requirements.txt
RUN python -m pip install --prefer-binary -r /app/backend/requirements.txt

# Includes FastAPI, migrations, seed data, startup scripts, and static website.
COPY backend/ /app/backend/

RUN chmod +x /app/backend/scripts/start.sh \
    && useradd --create-home --uid 10001 groe \
    && chown -R groe:groe /app

USER groe
WORKDIR /app/backend
EXPOSE 8000

CMD ["/app/backend/scripts/start.sh"]
