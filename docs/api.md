# API Reference

Полная спецификация API доступна по адресу: http://localhost:8000/docs (Swagger UI)

##  Base URL

```
Development: http://localhost:8000
Production:  https://api.example.com
```

##  Аутентификация

**Публичные endpoints** (без токена): `GET /api/projects`, `GET /api/projects/{id}`  
**Остальные endpoints** требуют JWT-токен в заголовке:

```
Authorization: Bearer <access_token>
```

### Регистрация

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response** `201 Created`:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "abc123...",
  "token_type": "bearer"
}
```

### Логин

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** `200 OK`:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "abc123...",
  "token_type": "bearer"
}
```

### Обновление токена

```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "abc123..."
}
```

**Response** `200 OK`:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "def456...",
  "token_type": "bearer"
}
```

### Выход (logout)

```http
POST /api/auth/logout
Content-Type: application/json

{
  "refresh_token": "abc123..."
}
```

**Response:** `204 No Content`

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
| GET | `/users/me` | Текущий пользователь (auth) |
| PATCH | `/users/me` | Обновить профиль (auth) |
| PUT | `/users/me/skills` | Обновить навыки (auth) |
| GET | `/users/{id}` | Публичный профиль (auth) |

#### GET /users/me — мой профиль

```
GET /api/users/me
Authorization: Bearer <token>
```

**Response** `200 OK`:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "bio": "Python developer",
  "github_url": "https://github.com/john",
  "linkedin_url": "https://linkedin.com/in/john",
  "portfolio_url": null,
  "experience_years": 5,
  "avatar_file_id": null,
  "resume_file_id": null,
  "user_role": "user",
  "is_active": true,
  "last_login_at": null,
  "created_at": "2026-06-25T14:01:51Z",
  "updated_at": "2026-06-25T14:34:34Z",
  "skills": [
    {"id": 1, "name": "Python"},
    {"id": 2, "name": "FastAPI"}
  ]
}
```

#### PATCH /users/me — обновить профиль

```
PATCH /api/users/me
Authorization: Bearer <token>
Content-Type: application/json
```

Все поля опциональны — можно отправить только те, что меняются:

```json
{
  "full_name": "John Updated",
  "bio": "Full-stack developer",
  "github_url": "https://github.com/john",
  "linkedin_url": "https://linkedin.com/in/john",
  "portfolio_url": "https://john.dev",
  "experience_years": 7
}
```

**Response** `200 OK` — полный `UserResponse` (как в GET /users/me)

#### PUT /users/me/skills — обновить навыки

```
PUT /api/users/me/skills
Authorization: Bearer <token>
Content-Type: application/json
```

Передаётся **полный** список ID навыков — старые удаляются, новые добавляются:

```json
{
  "skill_ids": [1, 2, 3]
}
```

**Response** `200 OK` — полный `UserResponse` с обновлённым `skills`

#### GET /users/{id} — публичный профиль

```
GET /api/users/1
Authorization: Bearer <token>
```

Публичный профиль — без полей `id`, `user_role`, `created_at`, `updated_at`:

```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "bio": "Python developer",
  "github_url": "https://github.com/john",
  "linkedin_url": null,
  "portfolio_url": null,
  "experience_years": 5,
  "avatar_file_id": null,
  "resume_file_id": null,
  "is_active": true,
  "last_login_at": null,
  "skills": [
    {"id": 1, "name": "Python"}
  ]
}
```

### Projects

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/projects` | Список проектов (пагинация, public) |
| POST | `/projects` | Создать проект (auth) |
| GET | `/projects/{id}` | Детали проекта (public) |
| PATCH | `/projects/{id}` | Обновить проект (auth, только owner) |
| DELETE | `/projects/{id}` | Удалить проект (auth, только owner) |

#### GET /projects — список проектов

```
GET /api/projects?offset=0&limit=20
```

Публичный список. `offset` (≥0, по умолч. 0) и `limit` (1–100, по умолч. 20) опциональны.

**Response** `200 OK`:
```json
[
  {
    "id": 1,
    "owner_id": 1,
    "title": "AI Chat Bot",
    "description": "Building a chat bot",
    "format": "remote",
    "payment_type": "volunteer",
    "status": "open",
    "created_at": "2026-06-25T14:49:39Z",
    "updated_at": "2026-06-25T14:49:48Z",
    "skills": [
      {"id": 1, "name": "Python"}
    ],
    "members": [
      {"user_id": 1, "role": "owner", "joined_at": "2026-06-25T14:49:39Z", "is_active": true}
    ]
  }
]
```

#### POST /projects — создать проект

```
POST /api/projects
Authorization: Bearer <token>
Content-Type: application/json
```

| Поле | Тип | Обязательное | Допустимые значения |
|------|-----|:---:|---------------------|
| `title` | string | да | 1–200 символов |
| `description` | string | да | 1–5000 символов |
| `format` | string | нет | `remote` (по умолч.), `office`, `hybrid` |
| `payment_type` | string | нет | `volunteer` (по умолч.), `paid`, `equity` |
| `skill_ids` | int[] | нет | ID существующих навыков |

```json
{
  "title": "AI Chat Bot",
  "description": "Building a chat bot with RAG",
  "format": "remote",
  "payment_type": "volunteer",
  "skill_ids": [1, 2, 3]
}
```

**Response** `201 Created` — полный `ProjectResponse` (owner автоматически добавлен в `members` с ролью `owner`)

#### GET /projects/{id} — детали проекта

```
GET /api/projects/1
```

Публичный доступ. Возвращает полный проект со скиллами и участниками.

**Response** `200 OK` — `ProjectResponse` (тот же формат, что в списке)

#### PATCH /projects/{id} — обновить проект

```
PATCH /api/projects/1
Authorization: Bearer <token>
Content-Type: application/json
```

Только владелец (owner) может обновлять. Все поля опциональны.

| Поле | Тип | Допустимые значения |
|------|-----|---------------------|
| `title` | string | 1–200 символов |
| `description` | string | 1–5000 символов |
| `format` | string | `remote`, `office`, `hybrid` |
| `payment_type` | string | `volunteer`, `paid`, `equity` |
| `status` | string | `draft`, `open`, `closed`, `archived` |
| `skill_ids` | int[] | полный список — заменяет текущие навыки |

```json
{
  "title": "AI Chat Bot v2",
  "status": "open",
  "skill_ids": [1, 2]
}
```

**Response** `200 OK` — обновлённый `ProjectResponse`

#### DELETE /projects/{id} — удалить проект

```
DELETE /api/projects/1
Authorization: Bearer <token>
```

Только владелец (owner). Проект и все связанные записи (участники, навыки) удаляются.

**Response:** `204 No Content`

### Feed & Swipes

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/feed` | Лента рекомендаций (auth) |
| POST | `/swipes` | Свайп (откликнуться на проект, auth) |
| GET | `/swipes/inbox` | Входящие отклики (auth, для owner) |
| PATCH | `/swipes/{id}/review` | Одобрить/отклонить (auth, только owner) |

#### GET /feed — лента рекомендаций

```
GET /api/feed?offset=0&limit=20
Authorization: Bearer <token>
```

Проекты, на которые пользователь ещё не откликался. Свои проекты исключены. `offset` (≥0, по умолч. 0) и `limit` (1–100, по умолч. 20) опциональны.

**Response** `200 OK` — массив `ProjectResponse` (тот же формат, что в `GET /projects`)

#### POST /swipes — откликнуться на проект

```
POST /api/swipes
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "project_id": 1,
  "message": "Хочу участвовать! У меня есть опыт с Python"
}
```

| Поле | Тип | Обязательное | Описание |
|------|-----|:---:|----------|
| `project_id` | int | да | ID проекта |
| `message` | string | нет | Сопроводительное сообщение |

Ошибки:
- `400` — нельзя откликнуться на свой проект
- `400` — повторный отклик на тот же проект (ограничение `uq_swipe_per_project`)

**Response** `201 Created`:
```json
{
  "id": 1,
  "user_id": 2,
  "project_id": 1,
  "message": "Хочу участвовать!",
  "status": "pending",
  "created_at": "2026-06-25T15:00:00Z",
  "reviewed_at": null
}
```

#### GET /swipes/inbox — входящие отклики

```
GET /api/swipes/inbox
Authorization: Bearer <token>
```

Все отклики на проекты, где текущий пользователь — owner. Сортировка по `created_at` (сначала новые).

**Response** `200 OK` — массив `SwipeResponse`:

```json
[
  {
    "id": 1,
    "user_id": 2,
    "project_id": 1,
    "message": "Хочу участвовать!",
    "status": "pending",
    "created_at": "2026-06-25T15:00:00Z",
    "reviewed_at": null
  }
]
```

#### PATCH /swipes/{id}/review — одобрить/отклонить

```
PATCH /api/swipes/1/review
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "status": "approved"
}
```

| Поле | Тип | Допустимые значения |
|------|-----|---------------------|
| `status` | string | `approved`, `rejected` |

Если `status = "approved"` — автоматически создаётся `Match` со статусом `active`.

Ошибки:
- `403` — только owner проекта может ревьюить
- `400` — отклик уже обработан

**Response** `200 OK`:
- При `approved` — `MatchResponse`
- При `rejected` — обновлённый `SwipeResponse`

```json
// При approved:
{
  "id": 1,
  "user_id": 2,
  "project_id": 1,
  "swipe_id": 1,
  "status": "active",
  "created_at": "2026-06-25T15:01:00Z",
  "closed_at": null
}

// При rejected:
{
  "id": 1,
  "user_id": 2,
  "project_id": 1,
  "message": "Хочу участвовать!",
  "status": "rejected",
  "created_at": "2026-06-25T15:00:00Z",
  "reviewed_at": "2026-06-25T15:05:00Z"
}
```

### Matches

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/matches` | Список матчей (auth) |
| GET | `/matches/{id}` | Детали матча (auth) |
| DELETE | `/matches/{id}` | Закрыть матч (auth) |

#### GET /matches — список матчей

```
GET /api/matches
Authorization: Bearer <token>
```

Все матчи, где пользователь — либо откликнувшийся разработчик, либо owner проекта. Сортировка по `created_at` (сначала новые).

**Response** `200 OK`:
```json
[
  {
    "id": 1,
    "user_id": 2,
    "project_id": 1,
    "swipe_id": 1,
    "status": "active",
    "created_at": "2026-06-25T15:01:00Z",
    "closed_at": null
  }
]
```

#### GET /matches/{id} — детали матча

```
GET /api/matches/1
Authorization: Bearer <token>
```

**Response** `200 OK` — `MatchResponse` (тот же формат, что в списке)

Ошибки:
- `403` — не являетесь участником матча

#### DELETE /matches/{id} — закрыть матч

```
DELETE /api/matches/1
Authorization: Bearer <token>
```

Закрывает матч (status → `closed`, `closed_at` = now).

Ошибки:
- `403` — не являетесь участником матча
- `400` — матч уже закрыт

**Response:** `204 No Content`

### Chat

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/chat/{match_id}/messages` | История сообщений (auth) |
| WS | `/ws/chat/{match_id}` | WebSocket чат в реальном времени |

#### GET /chat/{match_id}/messages — история сообщений

```
GET /api/chat/1/messages?offset=0&limit=50
Authorization: Bearer <token>
```

Только участники матча могут смотреть историю. Пагинация от старых к новым.

**Response** `200 OK`:
```json
[
  {
    "id": 1,
    "match_id": 1,
    "sender_id": 5,
    "content": "Привет! Готов обсудить проект",
    "is_read": false,
    "created_at": "2026-06-25T15:10:00Z"
  },
  {
    "id": 2,
    "match_id": 1,
    "sender_id": 4,
    "content": "Давай!",
    "is_read": false,
    "created_at": "2026-06-25T15:10:30Z"
  }
]
```

Ошибки:
- `403` — не являетесь участником матча
- `404` — матч не найден

#### WebSocket: ws://localhost:8000/ws/chat/{match_id}

```
ws://localhost:8000/ws/chat/1?token=<access_token>
```

Подключение с JWT в query param. Сервер проверяет:
- токен валидный и это access token
- пользователь — участник матча (`user_id` или `owner`)

**Отправка сообщения:**
```json
{
  "type": "message",
  "content": "Привет!"
}
```

**Получение (от себя и от собеседника):**
```json
{
  "type": "message",
  "id": 42,
  "match_id": 7,
  "sender_id": 3,
  "content": "Привет!",
  "created_at": "2026-06-25T15:10:30Z"
}
```

**Ошибка (неверный формат):**
```json
{
  "type": "error",
  "detail": "Invalid message format"
}
```

Коды закрытия:
- `4001` — невалидный токен / пользователь неактивен
- `4003` — не участник матча
- `4004` — матч не найден

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

### Регистрация и профиль

```bash
# 1. Регистрация
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@test.com","password":"pass123","full_name":"Dev User"}'

# 2. Сохранить токен
TOKEN="<access_token из ответа>"

# 3. Получить свой профиль
curl -s http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN"

# 4. Обновить профиль
curl -s -X PATCH http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bio":"Python dev","github_url":"https://github.com/dev","experience_years":3}'

# 5. Добавить навыки
curl -s -X PUT http://localhost:8000/api/users/me/skills \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill_ids":[1,2,3]}'
```

### Проекты

```bash
# 1. Создать проект
curl -s -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Chat Bot",
    "description": "Building a chat bot with RAG",
    "format": "remote",
    "payment_type": "volunteer",
    "skill_ids": [1, 2]
  }'

# 2. Список проектов
curl -s http://localhost:8000/api/projects?offset=0&limit=10

# 3. Детали проекта
curl -s http://localhost:8000/api/projects/1

# 4. Обновить проект (только owner)
curl -s -X PATCH http://localhost:8000/api/projects/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Title","status":"open"}'

# 5. Удалить проект (только owner)
curl -s -X DELETE http://localhost:8000/api/projects/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Feed, Swipes и Matches

```bash
# 0. Нужны два токена: owner (создаёт проект) и developer (откликается)
# Зарегистрировать owner'а
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@test.com","password":"pass123","full_name":"Project Owner"}'

# Сохранить токен owner'а
OWNER="<access_token owner'а>"

# Зарегистрировать разработчика
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@test.com","password":"pass123","full_name":"Developer"}'

# Сохранить токен разработчика
DEV="<access_token разработчика>"

# 1. Owner создаёт проект
curl -s -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer $OWNER" \
  -H "Content-Type: application/json" \
  -d '{"title":"Cool Project","description":"Need a Python dev","format":"remote","payment_type":"volunteer"}'

# 2. Developer смотрит ленту
curl -s http://localhost:8000/api/feed \
  -H "Authorization: Bearer $DEV"

# 3. Developer откликается на проект
curl -s -X POST http://localhost:8000/api/swipes \
  -H "Authorization: Bearer $DEV" \
  -H "Content-Type: application/json" \
  -d '{"project_id":1,"message":"Хочу участвовать!"}'

# 4. Owner проверяет входящие
curl -s http://localhost:8000/api/swipes/inbox \
  -H "Authorization: Bearer $OWNER"

# 5. Owner одобряет отклик (создаётся Match)
curl -s -X PATCH http://localhost:8000/api/swipes/1/review \
  -H "Authorization: Bearer $OWNER" \
  -H "Content-Type: application/json" \
  -d '{"status":"approved"}'

# 6. Список матчей (для обеих сторон)
curl -s http://localhost:8000/api/matches \
  -H "Authorization: Bearer $DEV"

curl -s http://localhost:8000/api/matches \
  -H "Authorization: Bearer $OWNER"

# 7. Детали матча
curl -s http://localhost:8000/api/matches/1 \
  -H "Authorization: Bearer $DEV"

# 8. Закрыть матч (любая сторона)
curl -s -X DELETE http://localhost:8000/api/matches/1 \
  -H "Authorization: Bearer $DEV"
```

### Чат

```bash
# 1. История сообщений матча
curl -s http://localhost:8000/api/chat/1/messages \
  -H "Authorization: Bearer $DEV"

# 2. WebSocket (через wscat — нужно установить: npm install -g wscat)
# В одной консоли (разработчик):
wscat -c "ws://localhost:8000/ws/chat/1?token=<DEV_TOKEN>"

# В другой консоли (owner):
wscat -c "ws://localhost:8000/ws/chat/1?token=<OWNER_TOKEN>"

# Отправка сообщения (в любой из консолей):
{"type": "message", "content": "Привет!"}
```