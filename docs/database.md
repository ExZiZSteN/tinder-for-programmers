# Схема базы данных

Полный SQL-файл схемы:

```text
db.sql
```

## ER-диаграмма

См. раздел **3.3** документа **«Архитектура системы»**.

---

# Основные таблицы

## `users`

Центральная таблица. Хранит данные аутентификации и общий профиль пользователя.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `BIGSERIAL PK` | Первичный ключ |
| `email` | `VARCHAR(255) UNIQUE` | Email пользователя |
| `password_hash` | `VARCHAR(255)` | Хэш пароля (bcrypt) |
| `role` | `user_role` | `user` \| `admin` |
| `full_name` | `VARCHAR(150)` | Полное имя |
| `bio` | `TEXT` | Описание профиля |
| `experience_years` | `SMALLINT` | Диапазон `0..50` |
| `embedding` | `vector(384)` | Эмбеддинг профиля |
| `avatar_file_id` | `BIGINT FK → files` | Аватар |
| `resume_file_id` | `BIGINT FK → files` | Резюме |

---

## `projects`

Проекты, создаваемые пользователями.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `BIGSERIAL PK` | Первичный ключ |
| `owner_id` | `BIGINT FK → users` | Владелец проекта |
| `title` | `VARCHAR(200)` | Название |
| `description` | `TEXT` | Описание |
| `format` | `project_format` | `remote` / `office` / `hybrid` |
| `payment_type` | `payment_type` | `volunteer` / `paid` / `equity` |
| `status` | `project_status` | `draft` / `open` / `closed` / `completed` / `archived` |
| `embedding` | `vector(384)` | Эмбеддинг проекта |

---

## `swipes`

Отклики пользователей на проекты.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `BIGSERIAL PK` | Первичный ключ |
| `user_id` | `BIGINT FK → users` | Пользователь |
| `project_id` | `BIGINT FK → projects` | Проект |
| `message` | `TEXT` | Необязательное сообщение |
| `status` | `swipe_status` | `pending` / `approved` / `rejected` / `withdrawn` |

### Ограничения

```sql
UNIQUE(user_id, project_id)
```

Один пользователь не может откликнуться на один и тот же проект дважды.

---

## `matches`

Создаются после одобрения отклика.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `BIGSERIAL PK` | Первичный ключ |
| `user_id` | `BIGINT FK → users` | Пользователь |
| `project_id` | `BIGINT FK → projects` | Проект |
| `swipe_id` | `BIGINT FK → swipes UNIQUE` | Один свайп = один матч |
| `status` | `match_status` | `active` / `completed` / `closed` |

---

## `messages`

Сообщения участников чата матча.

---

## `notifications`

Пользовательские уведомления.

---

## `files`

Метаданные файлов, размещённых в MinIO.

---

## `skills`

Справочник навыков.

---

## `user_skills`

Связь пользователей и навыков (**Many-to-Many**).

---

## `project_skills`

Связь проектов и навыков (**Many-to-Many**).

---

## `project_members`

Участники команды проекта.

---

## `refresh_tokens`

JWT Refresh-токены с поддержкой ротации.

---

# Индексы

## Векторные индексы (HNSW)

```sql
CREATE INDEX idx_users_embedding
ON users
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_projects_embedding
ON projects
USING hnsw (embedding vector_cosine_ops);
```

---

## Hot Path индексы

```sql
-- Входящие отклики владельца проекта
CREATE INDEX idx_swipes_project_pending
ON swipes(project_id, created_at DESC)
WHERE status = 'pending';

-- Непрочитанные уведомления
CREATE INDEX idx_notifications_unread
ON notifications(user_id, created_at DESC)
WHERE is_read = FALSE;

-- Полнотекстовый поиск по названию проектов
CREATE INDEX idx_projects_title_trgm
ON projects
USING gin(title gin_trgm_ops);
```

---

# Миграции

```bash
# Создать новую миграцию
make migrate-create msg="description"

# Применить все миграции
make migrate

# Откатить последнюю
docker compose exec backend alembic downgrade -1

# История миграций
docker compose exec backend alembic history
```

---

# Прогнозируемый объём данных (MVP)

| Таблица | Ожидаемый объём |
|----------|----------------:|
| `users` | ~10 тыс. записей (~10 МБ) |
| `projects` | ~5 тыс. записей (~5 МБ) |
| `swipes` | ~50 тыс. записей (~20 МБ) |
| `matches` | ~5 тыс. записей (~2 МБ) |
| `messages` | ~500 тыс. записей (~200 МБ) |
| `notifications` | ~1 млн записей (~300 МБ) |
| Векторы (`15 000 × 384 × 4 B`) | ~22 МБ |

---

## Итоговый прогноз

| Компонент | Размер |
|-----------|--------:|
| Общий объём БД (MVP) | **~600 МБ** |
