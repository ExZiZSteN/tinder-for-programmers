# Руководство разработчика

##  Структура проекта

```
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

##  Архитектурные принципы

### Слоистая архитектура backend

```
Request → Router (api/) → Service (services/) → Repository (repositories/) → DB
                ↓
            Pydantic-схемы (schemas/)
```

**Правила:**
- Router — только валидация и вызов сервиса, без бизнес-логики
- Service — бизнес-логика, оркестрация, транзакции
- Repository — только SQL-запросы, никакого бизнес-контекста
- Model — только описание таблицы, без логики

### Пример: создание свайпа

```python
# app/api/swipes.py — тонкий контроллер
@router.post('/', status_code=201)
async def create_swipe(
    data: SwipeCreate,
    user = Depends(get_current_user),
    service: SwipeService = Depends(get_swipe_service)
):
    return await service.create_swipe(user.id, data)

# app/services/swipe.py — бизнес-логика
class SwipeService:
    async def create_swipe(self, user_id: int, data: SwipeCreate):
        # 1. Проверить, что проект существует и открыт
        project = await self.project_repo.get(data.project_id)
        if project.status != 'open':
            raise BadRequestException('Project not open')
        
        # 2. Нельзя свайпать свой проект
        if project.owner_id == user_id:
            raise ForbiddenException('Cannot swipe own project')
        
        # 3. Создать свайп
        swipe = await self.swipe_repo.create(user_id=user_id, ...)
        
        # 4. Уведомить владельца
        await self.notif_service.notify_new_swipe(project.owner_id, swipe)
        
        return swipe

# app/repositories/swipe.py — работа с БД
class SwipeRepository:
    async def create(self, user_id: int, project_id: int, ...) -> Swipe:
        swipe = Swipe(user_id=user_id, project_id=project_id, ...)
        self.db.add(swipe)
        await self.db.commit()
        return swipe
```

##  Dependency Injection

FastAPI использует `Depends` для внедрения зависимостей:

```python
# app/core/deps.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_token(token)
    user = await db.get(User, payload['sub'])
    if not user or user.is_banned:
        raise HTTPException(401, 'Invalid token')
    return user

def get_swipe_service(db: AsyncSession = Depends(get_db)) -> SwipeService:
    return SwipeService(
        swipe_repo=SwipeRepository(db),
        project_repo=ProjectRepository(db),
        notif_service=NotificationService(db)
    )
```

##  Работа с БД

### Миграции

```bash
# Создать миграцию после изменения моделей
make migrate-create msg="add new field"

# Применить миграции
make migrate

# Откатить последнюю миграцию
docker compose exec backend alembic downgrade -1
```

### Добавление новой таблицы

1. Создать модель в `app/models/`
2. Импортировать в `app/models/__init__.py`
3. Создать миграцию: `make migrate-create msg="add X table"`
4. Применить: `make migrate`
5. Создать repository в `app/repositories/`
6. Создать service в `app/services/`
7. Создать router в `app/api/`
8. Подключить router в `app/api/router.py`

##  Frontend-соглашения

### Структура компонента

```typescript
// components/feed/FeedCard.tsx
import { FC } from 'react';
import { cn } from '@/utils/cn';

interface FeedCardProps {
  project: Project;
  onLike: () => void;
  onPass: () => void;
}

export const FeedCard: FC<FeedCardProps> = ({ project, onLike, onPass }) => {
  return (
    <div className={cn('bg-white rounded-lg shadow p-6')}>
      {/* ... */}
    </div>
  );
};
```

### Хуки

```typescript
// hooks/useFeed.ts — data fetching
export const useFeed = () => {
  return useInfiniteQuery({
    queryKey: ['feed'],
    queryFn: ({ pageParam }) => feedApi.getFeed(pageParam),
    getNextPageParam: (lastPage) => lastPage.next_cursor,
  });
};

// hooks/useSwipe.ts — mutations
export const useSwipe = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: SwipeCreate) => swipesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feed'] });
    },
  });
};
```

### State management

- **Server state** (данные с backend) → TanStack Query
- **Client state** (auth, UI) → Zustand
- **Form state** → React Hook Form + Zod
- **URL state** → React Router

##  Локальная разработка

### Backend

```bash
# Запустить backend с hot reload
docker compose exec backend uvicorn app.main:app --reload --host 0.0.0.0

# Войти в контейнер
docker compose exec backend bash

# Запустить pytest
docker compose exec backend pytest -v
```

### Frontend

```bash
# Запустить frontend с hot reload
docker compose exec frontend npm run dev

# Проверить типы
docker compose exec frontend npm run type-check

# Проверить lint
docker compose exec frontend npm run lint
```

##  Стиль кода

### Python

- **Line length:** 100 символов
- **Formatter:** ruff
- **Type hints:** обязательны для всех публичных функций
- **Docstrings:** Google-style для публичных API

### TypeScript

- **Strict mode:** включён
- **Formatter:** Prettier
- **Lint:** ESLint с recommended rules
- **Именование:** PascalCase для компонентов, camelCase для функций/переменных

##  Git Workflow

```bash
# 1. Создать ветку от main
git checkout -b feat/swipe-animations

# 2. Коммиты в conventional commits формате
git commit -m "feat(swipe): add animation on like"
git commit -m "fix(chat): fix message ordering"
git commit -m "docs(api): update endpoints description"

# 3. Push и создать PR
git push origin feat/swipe-animations
```

**Формат коммитов:**
- `feat:` — новая функциональность
- `fix:` — исправление бага
- `docs:` — документация
- `refactor:` — рефакторинг
- `test:` — тесты
- `chore:` — инфраструктура, зависимости