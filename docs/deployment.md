# Развёртывание

## Production-топология

```text
┌─────────────────────────────────────────────────────────────┐
│  Load Balancer (Nginx / Cloud LB)                           │
│  - SSL termination                                          │
│  - Health checks                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Backend       Backend       Backend      (N инстансов)
             │             │             │
             └─────────────┼─────────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        PostgreSQL       Redis         MinIO
```

---

# Docker Compose (Production)

```yaml
# docker-compose.prod.yml

version: "3.8"

services:
  db:
    image: pgvector/pgvector:pg16
    container_name: tinder-db

    environment:
      POSTGRES_DB: tinder_devs
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

    ports:
      - "5432:5432"

    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./backend/scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql

    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d tinder_devs"]
      interval: 5s
      timeout: 5s
      retries: 5

    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: tinder-redis

    ports:
      - "6379:6379"

    volumes:
      - redis-data:/data

    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

    restart: unless-stopped

  minio:
    image: minio/minio
    container_name: tinder-minio

    command: server /data --console-address ":9001"

    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin

    ports:
      - "9000:9000" # S3 API
      - "9001:9001" # Web Console

    volumes:
      - minio-data:/data

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 5s
      retries: 3

    restart: unless-stopped

  backend:
    build: ./backend
    container_name: tinder-backend

    env_file:
      - .env

    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/tinder_devs
      REDIS_URL: redis://redis:6379/0
      MINIO_ENDPOINT: minio:9000

    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy

    ports:
      - "8000:8000"

    volumes:
      - ./backend:/app

    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: tinder-frontend

    ports:
      - "5173:5173"

    volumes:
      - ./frontend:/app
      - /app/node_modules

    environment:
      - VITE_API_URL=http://localhost:8000/api
      - VITE_WS_URL=ws://localhost:8000

    command: npm run dev -- --host

    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:
  minio-data:
```

---

# SSL / HTTPS

```nginx
# nginx/nginx.conf

server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://frontend:3000;
    }

    location /api/ {
        proxy_pass http://backend:8000/;
    }

    location /ws/ {
        proxy_pass http://backend:8000/ws/;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

# Бэкапы

```bash
# Резервное копирование PostgreSQL
docker compose exec db pg_dump -U postgres tinder_devs > backup_$(date +%Y%m%d).sql

# Восстановление PostgreSQL
docker compose exec -T db psql -U postgres tinder_devs < backup.sql

# Резервное копирование MinIO
mc mirror myminio/uploads ./backups/minio/
```

## Регламент резервного копирования

| Компонент | Периодичность |
|-----------|---------------|
| PostgreSQL | Ежедневно в 00:00 |
| MinIO | Еженедельно |
| Хранение резервных копий | 30 дней |

---

# Мониторинг

## Health Checks

```text
GET /health    — liveness (проверка запуска приложения)
GET /ready     — readiness (проверка доступности БД, Redis и MinIO)
```

---

## Метрики

```yaml
# Интеграция в docker-compose.prod.yml

services:
  prometheus:
    image: prom/prometheus

    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana

    ports:
      - "3000:3000"
```

---

## Sentry

```python
# app/main.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

---

# Деплой

```bash
# 1. Сборка образов
docker compose -f docker-compose.prod.yml build

# 2. Публикация образов
docker tag backend registry.example.com/backend:v1.0
docker push registry.example.com/backend:v1.0

# 3. Обновление контейнеров
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# 4. Применение миграций
docker compose exec backend alembic upgrade head
```

---

# Переменные окружения (Production)

```env
# .env.production

APP_ENV=production
SECRET_KEY=strong-random-secret-key-at-least-64-bytes

DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/tinder_devs
REDIS_URL=redis://:password@redis:6379/0

JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=production-access-key
MINIO_SECRET_KEY=production-secret-key

SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

# План аварийного восстановления (Recovery)

При полном отказе продуктового сервера рекомендуется соблюдать следующий порядок действий.

1. Развернуть чистую операционную систему на новом сервере.
2. Восстановить базу данных PostgreSQL из последнего ежедневного дампа.
3. Восстановить данные MinIO из последней резервной копии.
4. Развернуть контейнеры приложения.

   ```bash
   docker compose up -d
   ```

5. Применить актуальные миграции.

   ```bash
   alembic upgrade head
   ```

6. Проверить работоспособность приложения через эндпоинты Health Checks.

---

## Целевые показатели

| Показатель | Значение |
|------------|----------|
| **RTO (Recovery Time Objective)** | ≤ 4 часа |
