# Руководство разработчика

## Структура проекта

```text
tinder-for-programmers/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── core/         # Конфиг, БД, безопасность, зависимости
│   │   ├── models/       # SQLAlchemy ORM-модели
│   │   ├── schemas/      # Pydantic DTO
│   │   ├── api/          # HTTP/WebSocket endpoints
│   │   ├── services/     # Бизнес-логика
│   │   ├── repositories/ # Работа с БД
│   │   ├── ml/           # ML-подсистема
│   │   ├── workers/      # Фоновые задачи (arq)
│   │   └── utils/        # Утилиты
│   ├── alembic/          # Миграции БД
│   ├── tests/            # pytest
│   └── Dockerfile
│
├── frontend/             # React frontend
│   ├── src/
│   │   ├── api/          # Axios client
│   │   ├── hooks/        # Custom hooks
│   │   ├── stores/       # Zustand stores
│   │   ├── components/   # UI-компоненты
│   │   ├── pages/        # Роуты
│   │   └── types/        # TypeScript типы
│   ├── package.json
│   └── Dockerfile
│
├── nginx/                # Reverse proxy
├── docs/                 # Документация
├── docker-compose.yml
└── Makefile
```

---

# Архитектурные принципы

## Слоистая архитектура Backend

```text
Request
    │
    ▼
Router (api/)
    │
    ▼
Service (services/)
    │
    ▼
Repository (repositories/)
    │
    ▼
Database

        │
        ▼
Pydantic Schemas (schemas/)
```

### Правила взаимодействия слоев

- **Router** — отвечает только за валидацию данных, авторизацию и вызов сервиса. Бизнес-логика отсутствует.
- **Service** — содержит бизнес-логику, оркестрацию подсистем и управление транзакциями.
- **Repository** — инкапсулирует SQL-запросы и не содержит бизнес-контекста.
- **Model** — описывает структуру таблиц базы данных без внутренней логики.

---

## Пример: создание свайпа

### Router

```python
# app/api/swipes.py

@router.post("/", status_code=201)
async def create_swipe(
    data: SwipeCreate,
    user=Depends(get_current_user),
    service: SwipeService = Depends(get_swipe_service),
):
    return await service.create_swipe(user.id, data)
```

### Service

```python
# app/services/swipe.py

class SwipeService:
    async def create_swipe(self, user_id: int, data: SwipeCreate):
        # 1. Проверить, что проект существует и открыт
        project = await self.project_repo.get(data.project_id)
        if project.status != "open":
            raise BadRequestException("Project not open")

        # 2. Нельзя свайпать собственный проект
        if project.owner_id == user_id:
            raise ForbiddenException("Cannot swipe own project")

        # 3. Создать запись свайпа
        swipe = await self.swipe_repo.create(
            user_id=user_id,
            ...
        )

        # 4. Отправить уведомление владельцу проекта
        await self.notif_service.notify_new_swipe(project.owner_id, swipe)

        return swipe
```

### Repository

```python
# app/repositories/swipe.py

class SwipeRepository:
    async def create(
        self,
        user_id: int,
        project_id: int,
        ...
    ) -> Swipe:
        swipe = Swipe(
            user_id=user_id,
            project_id=project_id,
            ...
        )

        self.db.add(swipe)
        await self.db.commit()

        return swipe
```

---

# Dependency Injection

Внедрение зависимостей в FastAPI реализуется через механизм `Depends`.

```python
# app/core/deps.py

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(token)

    user = await db.get(User, payload["sub"])

    if not user or user.is_banned:
        raise HTTPException(401, "Invalid token")

    return user


def get_swipe_service(
    db: AsyncSession = Depends(get_db),
) -> SwipeService:
    return SwipeService(
        swipe_repo=SwipeRepository(db),
        project_repo=ProjectRepository(db),
        notif_service=NotificationService(db),
    )
```

---

# Работа с базой данных

## Миграции

```bash
# Создать новую миграцию
make migrate-create msg="add new field"

# Применить все миграции
make migrate

# Откатить последнюю миграцию
docker compose exec backend alembic downgrade -1
```

## Алгоритм добавления новой таблицы

1. Создать модель в `app/models/`.
2. Импортировать модель в `app/models/__init__.py`.
3. Создать автомиграцию:

   ```bash
   make migrate-create msg="add X table"
   ```

4. Применить миграции:

   ```bash
   make migrate
   ```

5. Создать Repository в `app/repositories/`.
6. Создать Service в `app/services/`.
7. Создать Router в `app/api/`.
8. Подключить роутер в `app/api/router.py`.

---

# Frontend-соглашения

## Структура UI-компонента

```tsx
// components/feed/FeedCard.tsx

import { FC } from "react";
import { cn } from "@/utils/cn";

interface FeedCardProps {
  project: Project;
  onLike: () => void;
  onPass: () => void;
}

export const FeedCard: FC<FeedCardProps> = ({
  project,
  onLike,
  onPass,
}) => {
  return (
    <div className={cn("bg-white rounded-lg shadow p-6")}>
      {/* Контент компонента */}
    </div>
  );
};
```

---

## Кастомные хуки

### Получение данных

```tsx
// hooks/useFeed.ts

export const useFeed = () => {
  return useInfiniteQuery({
    queryKey: ["feed"],
    queryFn: ({ pageParam }) => feedApi.getFeed(pageParam),
    getNextPageParam: (lastPage) => lastPage.next_cursor,
  });
};
```

### Изменение данных

```tsx
// hooks/useSwipe.ts

export const useSwipe = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SwipeCreate) => swipesApi.create(data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["feed"],
      });
    },
  });
};
```

---

# Управление состоянием

| Тип состояния | Инструмент |
|---------------|------------|
| Server State | TanStack Query |
| Client State | Zustand |
| Form State | React Hook Form + Zod |
| URL State | React Router |

---

# Локальная разработка

## Backend

```bash
# Запустить backend с hot reload
docker compose exec backend uvicorn app.main:app --reload --host 0.0.0.0

# Открыть bash внутри контейнера
docker compose exec backend bash

# Запустить тесты
docker compose exec backend pytest -v
```

## Frontend

```bash
# Запустить dev-сервер
docker compose exec frontend npm run dev

# Проверить типы
docker compose exec frontend npm run type-check

# Проверить линтер
docker compose exec frontend npm run lint
```

---

# Стиль кода

## Python

- Максимальная длина строки — **100 символов**.
- Форматирование и линтинг — **ruff**.
- Аннотации типов обязательны.
- Документирование — **Google-style docstrings**.

## TypeScript

- Используется **strict mode**.
- Форматирование — **Prettier**.
- Линтинг — **ESLint**.
- Именование:
  - **PascalCase** — компоненты.
  - **camelCase** — функции, методы и переменные.

---

# Git Workflow

```bash
# 1. Создать новую ветку
git checkout -b feat/swipe-animations

# 2. Сделать коммит
git commit -m "feat(swipe): add animation on like"
git commit -m "fix(chat): fix message ordering"
git commit -m "docs(api): update endpoints description"

# 3. Отправить изменения
git push origin feat/swipe-animations
```

## Допустимые типы коммитов

| Тип | Назначение |
|------|------------|
| `feat:` | Новая функциональность |
| `fix:` | Исправление ошибок |
| `docs:` | Изменения документации |
| `refactor:` | Рефакторинг без изменения логики |
| `test:` | Добавление или изменение тестов |
| `chore:` | Конфигурация, зависимости, инфраструктура |
