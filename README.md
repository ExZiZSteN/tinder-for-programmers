# Tinder for programmers
Платформа для поиска разработчиками проектов через механизм взаимных свайпов с семантической рекомендацией

## Возможности
- Регистрация и авторизация (JWT)
- Профили разработчиков и владельцев проектов
- Создание и управление проектами
- Свайпы проектов (Tinder-like интерфейс)
- Взаимные мэтчи с автоматическим открытием чата
- Realtime-чат через WebSocket
- Семантическая рекомендательная система (Sentence Transformesr + pgvector)
- Realtime-уведомления
- Админ панель (SQLAdmin)
- Файловое хранилище (MinIO)

## Технологический стек
**Backend:** Python 3.13, FastAPI, SQLAlchemy 2.0, PostgreSQL 16 + pgvector, Redis, arq  
**Frontend:** React 19, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand  
**ML:** Sentence Transformers (paraphrase-multilingual-MiniLM-L12-v2)  
**Storage:** MinIO (S3-compatible)  
**Infra:** Docker Compose, Nginx, GitHub Actions

## 🚀 Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/ExZiZSteN/tinder-for-programmers
cd tinder-for-programmers

# 2. Скопировать env-файл
cp .env.example .env

# 3. Поднять Docker

docker compose up --build
docker compose run --rm backend alembic upgrade head
docker compose cp scripts/seed_skills.py backend:app/scripts/seed_skill.py
docker compose exec backend python scripts/seed_skills.py # наполнение навыков
docker compose exec db psql -U postgres -d tinder_devs
-- Конвертируем swipes
UPDATE swipes 
SET status = LOWER(status::text)::swipe_status;

-- Конвертируем matches
UPDATE matches 
SET status = LOWER(status::text)::match_status;

-- Проверяем результат
SELECT DISTINCT status FROM swipes;
SELECT DISTINCT status FROM matches;
\q
docker compose restart backend

```

## 📚 Документация

Полная документация находится в папке [`/docs`](./docs/README.md):

- [Быстрый старт](./docs/getting-started.md)
- [Руководство разработчика](./docs/development.md)
- [API Reference](./docs/api.md)
- [Архитектура системы](./docs/architecture.md)
- [Схема БД](./docs/database.md)
- [ML Pipeline](./docs/ml-pipeline.md)
- [Realtime](./docs/realtime.md)
- [Развёртывание](./docs/deployment.md)
- [Тестирование](./docs/testing.md)
- [Contributing](./docs/contributing.md)
- [Troubleshooting](./docs/troubleshooting.md)

## 🔗 Ссылки

- Backend (FastAPI): http://localhost:8000
- Frontend: http://localhost:5173
- API (Swagger): http://localhost:8000/docs
- Admin: http://localhost:8000/admin
- MinIO Console: http://localhost:9001
