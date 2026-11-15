# Macro Intelligence Lab

**Economic Intelligence. Market Insight. Research-Driven Decisions.**

A macro research platform that publishes forecasts scored in public. The
Sprint 1 foundation establishes the monorepo, backend scaffold, frontend
scaffold, database connection, JWT authentication, Docker workflow, and CI.

## Sprint status

- **Sprint 1 (current):** Foundation — monorepo, scaffolds, DB, auth, Docker, CI
- Sprint 2: Data model — reference tables, indicators, observations
- Sprint 3: ETL — FRED, World Bank, Yahoo ingestion
- Sprint 4: Public site + terminal shell
- ... see `docs/deliverables/`

## Quickstart

```bash
# 1. Clone
git clone https://github.com/<you>/macro-intelligence-lab.git
cd macro-intelligence-lab

# 2. Copy environment
cp .env.example .env

# 3. Bring up the stack
docker compose -f infra/docker-compose.yml up --build

# 4. Once up:
#    API:     http://localhost:8000/api/v1/health
#    OpenAPI: http://localhost:8000/api/v1/openapi.json  (dev only)
#    Web:     http://localhost:5173