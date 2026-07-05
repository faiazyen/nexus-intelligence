# syntax=docker/dockerfile:1
# NEXUS Intelligence backend — FastAPI on Python 3.12
# Multi-stage: deps compiled in a builder layer (cached off requirements.txt),
# slim runtime with a non-root user.

# ---------- Stage 1: dependency builder ----------
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Toolchain for any packages that need to compile from source.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependency layer is cached until requirements.txt changes.
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# curl is used by container healthchecks (compose + ECS).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system nexus && adduser --system --ingroup nexus nexus

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .
RUN chown -R nexus:nexus /app

USER nexus

EXPOSE 8000

# docker-compose overrides this to run "alembic upgrade head" first.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
