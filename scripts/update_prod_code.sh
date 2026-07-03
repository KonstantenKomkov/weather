#!/usr/bin/env bash
# Обновление prod: git fetch + reset --hard + пересборка и перезапуск web/celery.
# БД и .env на сервере не меняются.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SSH_HOST="${SSH_HOST:-deploy@your-server}"
SSH_KEY="${SSH_KEY:-$ROOT_DIR/deploy_key}"
if [[ "$SSH_KEY" == "~" ]]; then
    SSH_KEY="$HOME"
elif [[ "$SSH_KEY" == "~/"* ]]; then
    SSH_KEY="${HOME}${SSH_KEY:1}"
fi
SSH_CONTROL_PATH="${SSH_CONTROL_PATH:-/tmp/weather-ssh-%r@%h:%p}"
REMOTE_DIR="${REMOTE_DIR:-/opt/weather}"
GIT_BRANCH="${GIT_BRANCH:-master}"
PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-https://your-domain.example}"
HEALTH_WAIT_ATTEMPTS="${HEALTH_WAIT_ATTEMPTS:-30}"
HEALTH_WAIT_INTERVAL_SEC="${HEALTH_WAIT_INTERVAL_SEC:-2}"

DRY_RUN=0
SKIP_PUSH_CHECK=0
CI_MODE=0

usage() {
    cat <<'EOF'
Обновить prod-сервер: git fetch + reset --hard, docker build, up -d.

Использование:
  ./scripts/update_prod_code.sh [опции]
  make update-prod-code

Опции:
  -h, --help              эта справка
  -n, --dry-run           показать шаги без выполнения на сервере
  --skip-push-check       не проверять, что master запушена в origin
  --ci                    режим GitHub Actions

Переменные окружения:
  SSH_HOST, SSH_KEY, REMOTE_DIR, GIT_BRANCH, PUBLIC_BASE_URL

Миграции Django накатываются в docker-entrypoint-prod.sh при старте web/celery.
Подробнее: documents/update_prod.md
EOF
}

log() {
    printf '==> %s\n' "$*"
}

run() {
    if [[ "$DRY_RUN" -eq 1 ]]; then
        printf '[dry-run] %s\n' "$*"
        return 0
    fi
    "$@"
}

ssh_cmd() {
    ssh -i "$SSH_KEY" -o ControlPath="$SSH_CONTROL_PATH" "$SSH_HOST" "$@"
}

ensure_ssh_master() {
    if [[ "$DRY_RUN" -eq 1 ]]; then
        return 0
    fi
    if ssh -i "$SSH_KEY" -o ControlPath="$SSH_CONTROL_PATH" -O check "$SSH_HOST" >/dev/null 2>&1; then
        return 0
    fi
    local host_key_checking="accept-new"
    if [[ "$CI_MODE" -eq 1 ]]; then
        host_key_checking="yes"
    fi
    run ssh -i "$SSH_KEY" \
        -o ControlMaster=yes \
        -o ControlPath="$SSH_CONTROL_PATH" \
        -o ControlPersist=600 \
        -o "StrictHostKeyChecking=$host_key_checking" \
        -fN "$SSH_HOST"
}

ensure_ssh_key_loaded() {
    if [[ "$DRY_RUN" -eq 1 ]]; then
        return 0
    fi
    if [[ ! -f "$SSH_KEY" ]]; then
        echo "SSH-ключ не найден: $SSH_KEY" >&2
        exit 1
    fi
    chmod 600 "$SSH_KEY" 2>/dev/null || true
    if [[ "$CI_MODE" -eq 1 ]]; then
        return 0
    fi
    if ! ssh-add -l >/dev/null 2>&1; then
        echo "ssh-agent не запущен. Выполните: eval \"\$(ssh-agent -s)\" && ssh-add $SSH_KEY" >&2
        exit 1
    fi
}

check_local_git_pushed() {
    if [[ "$SKIP_PUSH_CHECK" -eq 1 ]]; then
        return 0
    fi
    log "Проверка: локальная $GIT_BRANCH синхронизирована с origin"
    git fetch origin "$GIT_BRANCH" >/dev/null 2>&1 || true
    local unpushed
    unpushed="$(git log "origin/$GIT_BRANCH..HEAD" --oneline 2>/dev/null | wc -l | tr -d ' ')"
    if [[ "$unpushed" != "0" ]]; then
        echo "Есть $unpushed непушнутых коммитов. Сначала: git push origin $GIT_BRANCH" >&2
        exit 1
    fi
}

remote_update() {
    log "Обновление на сервере ($REMOTE_DIR)"
    if [[ "$DRY_RUN" -eq 1 ]]; then
        return 0
    fi
    ssh_cmd "set -euo pipefail
cd '$REMOTE_DIR'
DC='docker compose -f docker-compose.prod.yml'

git fetch origin '$GIT_BRANCH'
git reset --hard 'origin/$GIT_BRANCH'
git clean -fd -e data/ -e .env

\$DC build web
\$DC up -d

for i in \$(seq 1 $HEALTH_WAIT_ATTEMPTS); do
  code=\$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health || true)
  if [ \"\$code\" = '200' ]; then
    echo \"health OK (attempt \$i)\"
    break
  fi
  if [ \"\$i\" -eq $HEALTH_WAIT_ATTEMPTS ]; then
    echo \"health check failed (last HTTP \$code)\" >&2
    \$DC logs --tail=40 web
    exit 1
  fi
  sleep $HEALTH_WAIT_INTERVAL_SEC
done

\$DC ps
docker builder prune -af
"
}

check_external_health() {
    if [[ "$DRY_RUN" -eq 1 ]] || [[ "$PUBLIC_BASE_URL" == "https://your-domain.example" ]]; then
        return 0
    fi
    log "Внешняя проверка $PUBLIC_BASE_URL/health"
    local code
    code="$(curl -s -o /dev/null -w '%{http_code}' "$PUBLIC_BASE_URL/health" || true)"
    if [[ "$code" != "200" ]]; then
        echo "Внешний health вернул HTTP $code" >&2
        exit 1
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h | --help) usage; exit 0 ;;
        -n | --dry-run) DRY_RUN=1; shift ;;
        --skip-push-check) SKIP_PUSH_CHECK=1; shift ;;
        --ci) CI_MODE=1; SKIP_PUSH_CHECK=1; shift ;;
        *) echo "Неизвестная опция: $1" >&2; usage >&2; exit 1 ;;
    esac
done

ensure_ssh_key_loaded
check_local_git_pushed
ensure_ssh_master
remote_update
check_external_health
log "Готово"
