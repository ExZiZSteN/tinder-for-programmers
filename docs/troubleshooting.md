# Проблема 1

Написан код для backend/app/repositories
Написан скрипт для проверки что все корректно
backend/check.py
backend/test_asyncpg.py

Должно все работать коректно но нет
Я получаю
```bash
🔌 Проверяю подключение к БД...
❌ Ошибка подключения: ConnectionDoesNotExistError: connection was closed in the middle of operation
```

**Как воспроизвести**
```bash
#В tinder-for-programmers/
docker compose up db redis -d
cmd /c "docker compose exec -T db psql -U postgres -d tinder_devs < db.sql"

cd backend
python check.py
```