# Схема базы данных

Полный SQL-файл схемы: [`db.sql`](../db.sql)

##  ER-диаграмма

См. раздел 3.3 документа [Архитектура системы](./architecture.md).

## 🗂 Основные таблицы

### users
Центральная таблица. Хранит аутентификационные данные и общий профиль.

| Поле | Тип | Описание |
|------|-----|----------|
| id | BIGSERIAL PK | |
| email | VARCHAR(255) UQ | |
| password_hash | VARCHAR(255) | bcrypt |
| role | user_role | 'user' \| 'admin' |
| full_name | VARCHAR(150) | |
| bio | TEXT | |
| experience_years | SMALLINT | 0..50 |
| embedding | vector(384) | Эмбеддинг профиля |
| avatar_file_id | BIGINT FK → files | |
| resume_file_id | BIGINT FK → files | |

### projects
Проекты, созданные пользователями.

| Поле | Тип | Описание |
|------|-----|----------|
| id | BIGSERIAL PK | |
| owner_id | BIGINT FK → users | Владелец |
| title | VARCHAR(200) | |
| description | TEXT | |
| format | project_format | remote/office/hybrid |
| payment_type | payment_type | volunteer/paid/equity |
| status | project_status | draft/open/closed/completed/archived |
| embedding | vector(384) | Эмбеддинг проекта |

### swipes
Отклики пользователей на проекты.

| Поле | Тип | Описание |
|------|-----|----------|
| id | BIGSERIAL PK | |
| user_id | BIGINT FK → users | |
| project_id | BIGINT FK → projects | |
| message | TEXT | Опциональное сообщение |
| status | swipe_status | pending/approved/rejected/withdrawn |
| UNIQUE(user_id, project_id) | | Нельзя свайпать дважды |

### matches
Взаимные согласия (создаются при одобрении свайпа).

| Поле | Тип | Описание |
|------|-----|----------|
| id | BIGSERIAL PK | |
| user_id | BIGINT FK → users | |
| project_id | BIGINT FK → projects | |
| swipe_id | BIGINT FK → swipes UQ | Один свайп = один матч |
| status | match_status | active/completed/closed |

### messages
Сообщения в чате матча.

### notifications
Уведомления пользователей.

### files
Метаданные файлов в MinIO.

### skills, user_skills, project_skills
Нормализованные навыки (many-to-many).

### project_members
Участники проекта (команда).

### refresh_tokens
JWT refresh-токены с ротацией.

##  Индексы

### Векторные (HNSW)
```sql
CREATE INDEX idx_users_embedding ON users 
    USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_projects_embedding ON projects 
    USING hnsw (embedding vector_cosine_ops);
```

### Hot path
```sql
-- Входящие отклики владельца
CREATE INDEX idx_swipes_project_pending ON swipes(project_id, created_at DESC)
    WHERE status = 'pending';

-- Непрочитанные уведомления
CREATE INDEX idx_notifications_unread ON notifications(user_id, created_at DESC)
    WHERE is_read = FALSE;

-- Полнотекстовый поиск по названию
CREATE INDEX idx_projects_title_trgm ON projects 
    USING gin(title gin_trgm_ops);
```

##  Миграции

```bash
# Создать новую миграцию
make migrate-create msg="description"

# Применить все миграции
make migrate

# Откатить последнюю
docker compose exec backend alembic downgrade -1

# Посмотреть историю
docker compose exec backend alembic history
```

## 📈 Объём данных (прогноз MVP)

| Таблица | Ожидаемый объём | Размер |
|---------|-----------------|--------|
| users | 10k | ~10 МБ |
| projects | 5k | ~5 МБ |
| swipes | 50k | ~20 МБ |
| matches | 5k | ~2 МБ |
| messages | 500k | ~200 МБ |
| notifications | 1M | ~300 МБ |
| **Векторы** | 15k × 384 × 4B | ~22 МБ |
| **Итого** | | ~600 МБ |