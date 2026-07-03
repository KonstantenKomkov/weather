.PHONY: help build build-prod up up-prod down restart logs logs-web logs-db ps shell db-shell migrate test lint format get-weather clear-cities clean env frontend-install frontend-dev frontend-build ci update-prod-code

DOCKER_COMPOSE = docker compose
DOCKER_COMPOSE_PROD = docker compose -f docker-compose.prod.yml
WEB_SERVICE = web
DB_SERVICE = db

help:
	@echo "Weather — доступные команды:"
	@echo ""
	@echo "  make env              — создать .env из .env.example"
	@echo "  make build            — собрать Docker образы (dev)"
	@echo "  make build-prod       — собрать production-образ (Vite + gunicorn)"
	@echo "  make up               — запустить все сервисы (dev)"
	@echo "  make up-prod          — запустить prod-стек"
	@echo "  make down             — остановить все сервисы"
	@echo "  make restart          — перезапустить все сервисы"
	@echo "  make logs             — логи всех сервисов"
	@echo "  make logs-web         — логи Django"
	@echo "  make logs-db          — логи PostgreSQL"
	@echo "  make ps               — статус контейнеров"
	@echo "  make shell            — bash в контейнере web"
	@echo "  make db-shell         — psql в контейнере БД"
	@echo "  make migrate          — применить миграции"
	@echo "  make test             — pytest"
	@echo "  make lint             — ruff check"
	@echo "  make format           — ruff format"
	@echo "  make ci               — lint + pytest (как в GitHub Actions)"
	@echo "  make frontend-install — npm ci в mainapp/"
	@echo "  make frontend-dev     — Vite dev-сервер (прокси /api → :8000)"
	@echo "  make frontend-build   — production-сборка React → mainapp/build/"
	@echo "  make get-weather      — запустить парсер rp5.ru"
	@echo "  make clear-cities     — очистить cities.txt"
	@echo "  make clean            — удалить контейнеры и тома"
	@echo "  make update-prod-code — обновить код на prod-сервере (см. documents/update_prod.md)"
	@echo ""

env:
	@if [ ! -f .env ]; then cp .env.example .env && echo "Создан .env из .env.example"; else echo ".env уже существует"; fi

build:
	$(DOCKER_COMPOSE) build

build-prod:
	$(DOCKER_COMPOSE_PROD) build

up: env
	@mkdir -p .docker/postgres_data
	$(DOCKER_COMPOSE) up -d

up-prod: env
	@mkdir -p data/postgres
	$(DOCKER_COMPOSE_PROD) up -d

down:
	$(DOCKER_COMPOSE) down

restart:
	$(DOCKER_COMPOSE) restart

logs:
	$(DOCKER_COMPOSE) logs -f

logs-web:
	$(DOCKER_COMPOSE) logs -f $(WEB_SERVICE)

logs-db:
	$(DOCKER_COMPOSE) logs -f $(DB_SERVICE)

ps:
	$(DOCKER_COMPOSE) ps

shell:
	$(DOCKER_COMPOSE) exec $(WEB_SERVICE) /bin/bash

db-shell:
	$(DOCKER_COMPOSE) exec $(DB_SERVICE) psql -U $${POSTGRES_USER:-weather_user} -d $${POSTGRES_DB:-weather_db}

migrate:
	$(DOCKER_COMPOSE) exec $(WEB_SERVICE) python manage.py migrate

test:
	$(DOCKER_COMPOSE) exec $(WEB_SERVICE) pytest

lint:
	$(DOCKER_COMPOSE) exec $(WEB_SERVICE) ruff check .

format:
	$(DOCKER_COMPOSE) exec $(WEB_SERVICE) ruff format .

ci:
	$(DOCKER_COMPOSE) exec $(WEB_SERVICE) ruff check .
	$(DOCKER_COMPOSE) exec $(WEB_SERVICE) pytest -q

frontend-install:
	cd mainapp && npm ci

frontend-dev:
	cd mainapp && npm run dev

frontend-build:
	cd mainapp && npm ci && npm run build

get-weather:
	$(DOCKER_COMPOSE) exec $(WEB_SERVICE) python manage.py get_weather

clear-cities:
	$(DOCKER_COMPOSE) exec $(WEB_SERVICE) python manage.py clear_cities

clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans

update-prod-code:
	@chmod +x scripts/update_prod_code.sh
	./scripts/update_prod_code.sh $(if $(dry_run),--dry-run,) $(if $(skip_push_check),--skip-push-check,)
