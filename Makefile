# Macro Intelligence Lab — local development commands.
# On Windows without `make`, run the underlying `docker compose ...` commands directly.

COMPOSE := docker compose -f infra/docker-compose.yml

.PHONY: help up down rebuild migrate logs shell-api shell-db test test-api test-web lint clean

help:
	@echo "Targets:"
	@echo "  make up          Start the full stack (db + migrate + api + web)"
	@echo "  make down        Stop the stack"
	@echo "  make rebuild     Rebuild images with --no-cache"
	@echo "  make migrate     Run Alembic migrations"
	@echo "  make logs        Tail all service logs"
	@echo "  make shell-api   Open a shell in the running API container"
	@echo "  make shell-db    psql into the running Postgres"
	@echo "  make test        Run all tests (api + web)"
	@echo "  make test-api    Run backend tests only"
	@echo "  make test-web    Run frontend tests only"
	@echo "  make lint        Run all linters"
	@echo "  make clean       Remove containers and volumes"

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

rebuild:
	$(COMPOSE) build --no-cache api web

migrate:
	$(COMPOSE) run --rm migrate

logs:
	$(COMPOSE) logs -f

shell-api:
	$(COMPOSE) exec api bash

shell-db:
	$(COMPOSE) exec postgres psql -U mil -d mil

test: test-api test-web

test-api:
	$(COMPOSE) run --rm --no-deps api pytest

test-web:
	$(COMPOSE) run --rm --no-deps web pnpm test --run

lint:
	$(COMPOSE) run --rm --no-deps api ruff check src tests
	$(COMPOSE) run --rm --no-deps web pnpm lint

clean:
	$(COMPOSE) down -v