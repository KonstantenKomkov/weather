# Обновление prod-кода

Скрипт [`scripts/update_prod_code.sh`](../scripts/update_prod_code.sh) выполняет на сервере:

1. `git fetch` + `git reset --hard origin/master`
2. `docker compose -f docker-compose.prod.yml build web`
3. `docker compose -f docker-compose.prod.yml up -d`
4. Проверка `GET /health` на `127.0.0.1:8000`

БД (`data/postgres/`) и `.env` на сервере **не перезаписываются**.

## Локальный запуск

```bash
# 1. Закоммитить и запушить
git push origin master

# 2. Настроить переменные (или export)
export SSH_HOST=deploy@your-server
export SSH_KEY=~/.ssh/deploy_key
export REMOTE_DIR=/opt/weather
export PUBLIC_BASE_URL=https://your-domain.example

# 3. Обновить prod
make update-prod-code

# dry-run
make update-prod-code dry_run=1
```

## GitHub Actions

Workflow `.github/workflows/deploy.yml` — push в `master` или `workflow_dispatch`.

Secrets в репозитории:

| Secret | Описание |
|---|---|
| `DEPLOY_SSH_KEY` | приватный SSH-ключ |
| `DEPLOY_HOST` | IP или hostname |
| `DEPLOY_USER` | пользователь SSH (например `deploy`) |

## Первичная настройка сервера

См. [deployment.md](deployment.md): Docker, `.env`, `make up-prod`, nginx.

Рекомендуемый каталог на сервере: `/opt/weather` (клон репозитория).

## Откат

```bash
ssh deploy@server
cd /opt/weather
git log -5 --oneline
git reset --hard <commit>
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d
```

При необходимости — восстановление БД из дампа (`pg_dump` / `pg_restore`).
