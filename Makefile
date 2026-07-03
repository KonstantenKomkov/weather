.PHONY: help build up down restart logs logs-web logs-db ps shell db-shell migrate test lint format get-weather clear-cities clean env

DOCKER_COMPOSE = docker compose
WEB_SERVICE = web
DB_SERVICE = db

help:
	@echo "Weather — доступные команды:"
	@echo ""
	@echo "  make env              — создать .env из .env.example"
	@echo "  make build            — собрать Docker образы"
	@echo "  make up               — запустить все сервисы"
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
	@echo "  make get-weather      — запустить парсер rp5.ru"
	@echo "  make clear-cities     — очистить cities.txt"
	@echo "  make clean            — удалить контейнеры и тома"
	@echo ""

env:
	@if [ ! -f .env ]; then cp .env.example .env && echo "Создан .env из .env.example"; else echo ".env уже существует"; fi

build:
	$(DOCKER_COMPOSE) build

up: env
	@mkdir -p .docker/postgres_data
	$(DOCKER_COMPOSE) up -d

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

get-weather:
	$(DOCKER_COMPOSE) exec $(WEB_SERVICE) python manage.py get_weather

clear-cities:
	$(DOCKER_COMPOSE) exec $(WEB_SERVICE) python manage.py clear_cities

clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans
