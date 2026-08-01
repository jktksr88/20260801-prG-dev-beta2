FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend

# Install frontend dependencies in a cacheable layer. package*.json works
# whether or not a package-lock.json has been generated yet.
COPY frontend/package*.json ./
RUN npm install --include=dev --no-audit --no-fund

# Copy every frontend build input, including tsconfig.app.json.
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/backend/requirements.txt

COPY backend/ /app/backend/
COPY --from=frontend-build /app/frontend/dist /app/backend/app/static

RUN chmod +x /app/backend/scripts/start.sh \
    && useradd --create-home --uid 10001 groe \
    && chown -R groe:groe /app

USER groe
WORKDIR /app/backend
EXPOSE 8000
CMD ["/app/backend/scripts/start.sh"]
