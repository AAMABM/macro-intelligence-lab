# syntax=docker/dockerfile:1.7
# ----------------------------------------------------------------
# Stage 1: base — Python + system libs shared by api and worker
# ----------------------------------------------------------------
FROM python:3.12.7-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ----------------------------------------------------------------
# Stage 2: deps — install runtime requirements
# ----------------------------------------------------------------
FROM base AS deps

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# ----------------------------------------------------------------
# Stage 3: api — lean runtime
# ----------------------------------------------------------------
FROM base AS api

COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY scripts/ ./scripts/

ENV PYTHONPATH="/app/src"

RUN useradd --create-home --uid 10001 mil && chown -R mil:mil /app
USER mil

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/v1/health/live || exit 1

CMD ["uvicorn", "macro_api.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips=*"]

# ----------------------------------------------------------------
# Stage 4: worker — reserved for Sprint 3 (ETL/forecasting)
# ----------------------------------------------------------------
FROM base AS worker

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/

ENV PYTHONPATH="/app/src:/app"

RUN useradd --create-home --uid 10001 mil && chown -R mil:mil /app
USER mil

CMD ["python", "-c", "print('worker not implemented until Sprint 3'); exit 0"]