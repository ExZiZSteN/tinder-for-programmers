# Быстрый старт

Этот гайд поможет развернуть проект локально за 10 минут.

## Требования

- **Docker** 24+ и **Docker Compose** 2.20+
- **Make** (опционально, но рекомендуется)
- **Node.js** 20+ (только если нужно запускать frontend вне Docker)
- **Python** 3.13 (только если нужно запускать backend вне Docker)

##  Установка

### 1. Клонирование репозитория

```bash
git clone <repo-url>
cd tinder-for-devs
```

### 2. Конфигурация

Скопируйте пример env-файла:

```bash
cp .env.example .env
```

Основные переменные (по умолчанию уже настроены для dev):

```bash
# App
APP_ENV=development
SECRET_KEY=change-me-in-production

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/tinder_devs

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# ML
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIM=384
```

### 3. Запуск сервисов

```bash
make up
```

Или без make:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 4. Применение миграций

```bash
make migrate
```

### 5. Сидирование тестовых данных

```bash
make seed
```

Создаст тестовых пользователей и проекты:
- `dev@example.com` / `password` — разработчик
- `owner@example.com` / `password` — владелец проекта
- `admin@example.com` / `password` — администратор

### 6. Генерация эмбеддингов

```bash
make embed
```

Это создаст векторные представления для всех профилей и проектов.

##  Проверка

Откройте в браузере:

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:5173 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Admin Panel | http://localhost:8000/admin |
| MinIO Console | http://localhost:9001 |

##  Полезные команды

```bash
make up          # Поднять все сервисы
make down        # Остановить сервисы
make logs <svc>  # Логи конкретного сервиса
make migrate     # Применить миграции
make test        # Запустить тесты
make lint        # Проверить код
make seed        # Сидировать тестовые данные
make embed       # Сгенерировать эмбеддинги
make reset       # Полный сброс (осторожно!)
```

##  Что делать, если что-то не работает?

См. [Troubleshooting](./troubleshooting.md).