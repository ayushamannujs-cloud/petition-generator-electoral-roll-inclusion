# One image serving both the UI and the API, same as run.sh does locally:
# build the frontend, then let FastAPI serve frontend/dist alongside /api.

FROM node:24-slim AS frontend
WORKDIR /src/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/app backend/app
# main.py looks for the build at <repo>/frontend/dist, so keep that layout.
COPY --from=frontend /src/frontend/dist frontend/dist

WORKDIR /srv/backend
# Render injects PORT; 2026 is the local default.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-2026}"]
