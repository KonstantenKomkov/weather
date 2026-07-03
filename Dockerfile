FROM node:20-alpine AS frontend

WORKDIR /frontend

COPY mainapp/package.json mainapp/package-lock.json ./
RUN npm ci

COPY mainapp/ ./
RUN npm run build


FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


FROM base AS prod

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=frontend /frontend/build /app/mainapp/build

RUN chmod +x docker-entrypoint.sh docker-entrypoint-prod.sh

EXPOSE 8000

CMD ["sh", "/app/docker-entrypoint-prod.sh", "gunicorn", "weather.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]


FROM base AS dev

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

CMD ["gunicorn", "weather.wsgi:application", "--bind", "0.0.0.0:8000"]
