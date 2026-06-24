# API Reference

Полная спецификация API доступна по адресу: http://localhost:8000/docs (Swagger UI)

##  Base URL

```
Development: http://localhost:8000
Production:  https://api.example.com
```

##  Аутентификация

Все endpoints (кроме `/auth/*`) требуют JWT-токен в заголовке:

```
Authorization: Bearer <access_token>
```

### Получение токена

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "abc123...",
  "token_type": "bearer"
}
```

### Обновление токена

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "abc123..."
}
```

##  REST Endpoints

### Auth

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация |
| POST | `/auth/login` | Логин |
| POST | `/auth/refresh` | Обновление access token |
| POST | `/auth/logout` | Logout (отзыв refresh token) |

### Users & Profile

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/me` | Текущий пользователь |
| PATCH | `/me` | Обновить профиль |
| GET | `/users/{id}` | Публичный профиль |

### Projects

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/projects` | Список проектов (пагинация) |
| POST | `/projects` | Создать проект |
| GET | `/projects/{id}` | Детали проекта |
| PATCH | `/projects/{id}` | Обновить проект |
| DELETE | `/projects/{id}` | Удалить проект |

### Feed & Swipes

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/feed` | Лента рекомендаций |
| POST | `/swipes` | Свайп (лайк) |
| GET | `/swipes/inbox` | Входящие отклики (для владельца) |
| PATCH | `/swipes/{id}/review` | Одобрить/отклонить |

### Matches

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/matches` | Список матчей |
| GET | `/matches/{id}` | Детали матча |
| DELETE | `/matches/{id}` | Закрыть матч |

### Chat

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/chat/{match_id}/messages` | История сообщений |

### Notifications

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/notifications` | Список уведомлений |
| PATCH | `/notifications/{id}/read` | Отметить прочитанным |

### Files

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/upload` | Получить presigned URL для загрузки |
| GET | `/files/{id}` | Получить presigned URL для скачивания |

## 🔌 WebSocket Endpoints

### Chat

```
ws://localhost:8000/ws/chat/{match_id}?token=<jwt>
```

**Отправка сообщения:**
```json
{
  "type": "message",
  "content": "Hello!"
}
```

**Получение сообщения:**
```json
{
  "type": "message",
  "id": 42,
  "match_id": 7,
  "sender_id": 3,
  "content": "Hello!",
  "created_at": "2026-06-24T10:15:30Z"
}
```

### Notifications

```
ws://localhost:8000/ws/notifications?token=<jwt>
```

**Формат уведомлений:**
```json
{
  "type": "new_swipe",
  "payload": {
    "swipe_id": 42,
    "developer_name": "John Doe",
    "project_title": "My Cool Project"
  },
  "created_at": "2026-06-24T10:15:30Z"
}
```

##  Формат ответов

### Успех

```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150
  }
}
```

### Ошибка

```json
{
  "error": "NOT_FOUND",
  "detail": "Project 42 not found"
}
```

## 🚦 Rate Limiting

| Endpoint | Лимит |
|----------|-------|
| `/auth/login` | 10 req/min per IP |
| `/auth/register` | 5 req/min per IP |
| Остальные | 100 req/min per user |
| WebSocket | 30 msg/sec per connection |

##  Примеры

### Создать проект

```bash
curl -X POST http://localhost:8000/projects \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Chat Bot",
    "description": "Building an AI chat bot with RAG",
    "requirements": ["Python", "LLM experience"],
    "tech_stack": ["FastAPI", "PostgreSQL", "Redis"],
    "format": "remote",
    "payment_type": "paid"
  }'
```

### Получить ленту рекомендаций

```bash
curl http://localhost:8000/feed \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "data": [
    {
      "id": 42,
      "title": "AI Chat Bot",
      "description": "...",
      "tech_stack": ["FastAPI", "PostgreSQL"],
      "score": 0.87
    }
  ]
}
```