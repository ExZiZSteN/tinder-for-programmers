# Развёртывание

##  Production-топология

```
┌─────────────────────────────────────────────────────────────┐
│  Load Balancer (Nginx / Cloud LB)                           │
│  - SSL termination                                          │
│  - Health checks                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Backend      Backend      Backend      (N инстансов)
              │            │            │
              └────────────┼────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         PostgreSQL    Redis        MinIO
```

##  Docker Compose (production)

```yaml
# docker-compose.prod.yml
services:
  # ============================================================
  # PostgreSQL + pgvector
  # ============================================================
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

  # ============================================================
  # Redis
  # ============================================================
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

  # ============================================================
  # MinIO (S3-compatible storage)
  # ============================================================
  minio:
    image: minio/minio
    container_name: tinder-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"   # S3 API
      - "9001:9001"   # Web Console
    volumes:
      - minio-data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: unless-stopped

  # ============================================================
  # Backend (FastAPI)
  # ============================================================
  backend:
    build: ./backend
    container_name: tinder-backend
    env_file:
      - .env
    environment:
      # Переопределяем хосты для Docker-сети
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

  # ============================================================
  # Frontend (React + Vite)
  # ============================================================
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

# ============================================================
# Volumes
# ============================================================
volumes:
  postgres-data:
  redis-data:
  minio-data:
```

##  SSL/HTTPS

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

##  Бэкапы

```bash
# PostgreSQL
docker compose exec db pg_dump -U postgres tinder_devs > backup_$(date +%Y%m%d).sql

# Восстановление
docker compose exec -T db psql -U postgres tinder_devs < backup.sql

# MinIO
mc mirror myminio/uploads ./backups/minio/
```

**Рекомендуемый график:**
- PostgreSQL: ежедневно в 00:00
- MinIO: еженедельно
- Хранение: 30 дней

##  Мониторинг

### Health checks

```
GET /health     — liveness (приложение запущено)
GET /ready      — readiness (БД, Redis, MinIO доступны)
```

### Метрики (опционально)

```yaml
# docker-compose.prod.yml
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

### Sentry

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

##  Деплой-процесс

```bash
# 1. Собрать образы
docker compose -f docker-compose.prod.yml build

# 2. Запушить в registry
docker tag backend registry.example.com/backend:v1.0
docker push registry.example.com/backend:v1.0

# 3. На сервере
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# 4. Применить миграции
docker compose exec backend alembic upgrade head
```

## 🔧 Переменные окружения (production)

```bash
# .env.production
APP_ENV=production
SECRET_KEY=<strong-random-secret>

DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/tinder_devs
REDIS_URL=redis://:password@redis:6379/0

JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=<access-key>
MINIO_SECRET_KEY=<secret-key>

SENTRY_DSN=https://xxx@sentry.io/xxx
```

##  Recovery

**Сценарий:** полный отказ сервера

1. Поднять новый сервер
2. Восстановить БД из последнего бэкапа
3. Восстановить MinIO из бэкапа
4. Развернуть приложение: `docker compose up -d`
5. Применить миграции: `alembic upgrade head`
6. Проверить health checks

**Целевое время восстановления:** ≤ 4 часа
