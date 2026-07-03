# Production deployment

Образец по мотивам `farming_backend`. Prod-окружение без bind-mount исходников: frontend собирается в Docker, статика — через WhiteNoise.

## Требования

- Docker и Docker Compose на сервере
- Файл `.env` (скопировать из `.env.example`, задать `SECRET_KEY`, пароли, `DEBUG=false`, `ALLOWED_HOSTS`)

## Первый запуск

```bash
cp .env.example .env
# отредактировать .env

mkdir -p data/postgres
make build-prod
make up-prod
```

Проверка:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/api/docs/
```

## Отличия prod от dev

| | dev (`docker-compose.yml`) | prod (`docker-compose.prod.yml`) |
|---|---|---|
| Образ | target `dev` | target `prod` (multi-stage + Vite build) |
| Код | bind-mount `.:/app` | только из образа |
| Gunicorn | `--reload` | 2 workers |
| PostgreSQL | порт 5433 наружу | только docker-сеть |
| Web | `0.0.0.0:8000` | `127.0.0.1:8000` (nginx снаружи) |
| Статика | из `mainapp/build/` локально | `collectstatic` + WhiteNoise в entrypoint |

## Nginx (рекомендуется)

Проксировать на `127.0.0.1:8000`:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Обновление кода

```bash
git pull
make build-prod
make up-prod
```

Миграции применяются автоматически в `docker-entrypoint-prod.sh`.

См. также [update_prod.md](update_prod.md) — обновление кода на уже настроенном сервере.

## GitHub Actions deploy (опционально)

Workflow `.github/workflows/deploy.yml` — **только вручную** (`workflow_dispatch`).  
Secrets: `DEPLOY_SSH_KEY`, `DEPLOY_HOST`, `DEPLOY_USER`.  
Подробнее: [update_prod.md](update_prod.md).
