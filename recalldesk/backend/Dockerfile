FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# curl is used by the compose healthcheck
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies. The full `hindsight-all` bundle (PyTorch + local embedding
# models, ~9 GB) is intentionally skipped here: in Docker the app talks to the
# dedicated `hindsight` service over HTTP, so only `hindsight-client` is needed.
COPY requirements.txt ./
RUN grep -v '^hindsight-all' requirements.txt > /tmp/requirements-docker.txt \
    && pip install -r /tmp/requirements-docker.txt

COPY app ./app

# Application data (SQLite) lives on a mounted volume at /app/data
RUN mkdir -p /app/data

EXPOSE 8000

# Seed synthetic demo data on first start (no-op-ish if already seeded), then serve.
CMD ["sh", "-c", "python -m app.database.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
