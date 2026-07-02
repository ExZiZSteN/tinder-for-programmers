# Архитектура системы «Tinder for Developers»

**Версия:** 1.0  
**Дата:** Июнь 2026  
**Статус:** Утверждено

---

## Содержание

1. [Введение](#1-введение)
2. [Принципы архитектуры](#2-принципы-архитектуры)
3. [Общая архитектура](#3-общая-архитектура)
4. [Стек технологий](#4-стек-технологий)
5. [Архитектура Backend](#5-архитектура-backend)
6. [Архитектура Frontend](#6-архитектура-frontend)
7. [ML Pipeline](#7-ml-pipeline)
8. [Realtime-коммуникации](#8-realtime-коммуникации)
9. [Архитектура данных](#9-архитектура-данных)
10. [API](#10-api)
11. [Безопасность](#11-безопасность)
12. [Масштабируемость и производительность](#12-масштабируемость-и-производительность)
13. [Развёртывание](#13-развёртывание)
14. [Сквозные сценарии](#14-сквозные-сценарии)

---

## 1. Введение

### 1.1. Назначение документа

Документ описывает архитектуру программного сервиса **«Tinder for Developers»** — платформы для поиска разработчиками проектов через механизм взаимных свайпов с применением семантической рекомендательной системы.

Документ предназначен для:
- разработчиков команды — как руководство по реализации;
- технического руководителя — как основа для архитектурных решений;
- специалистов по сопровождению — как основа для эксплуатации и развития.

### 1.2. Область применения

Архитектура описывает **MVP-версию** системы, ориентированную на веб-платформу. Предусмотрена возможность последующего расширения для мобильного приложения и перехода к микросервисной архитектуре.

---

## 2. Принципы архитектуры

| Принцип | Описание |
|---------|----------|
| **Разделение ответственности** | Каждый компонент решает одну задачу; слои backend изолированы |
| **Слабая связанность** | Компоненты взаимодействуют через чёткие контракты (REST, WebSocket, очереди) |
| **Масштабируемость** | Stateless-сервисы, горизонтальное масштабирование, внешнее состояние в Redis/БД |
| **Безопасность по умолчанию** | Валидация на всех уровнях, минимальные привилегии, защита данных |
| **Наблюдаемость** | Структурные логи, метрики, трекинг запросов (correlation ID) |
| **Тестируемость** | Внедрение зависимостей, изоляция слоёв, моки для внешних сервисов |
| **Эволюционируемость** | Модульная структура, позволяющая заменять компоненты без переписывания |

---

## 3. Общая архитектура

### 3.1. Контейнерная диаграмма

```
┌─────────────────────────────────────────────────────────────┐
│                        Пользователь                          │
│                  (браузер, HTTPS/WSS)                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Nginx (Reverse Proxy)                      │
│              SSL termination, Rate limiting                  │
└─────┬─────────────────┬─────────────────┬───────────────────┘
      │                 │                 │
      ▼                 ▼                 ▼
┌──────────┐    ┌──────────────┐    ┌──────────────┐
│ Frontend │    │   Backend    │    │   Backend    │
│ (React)  │    │   REST API   │    │  WebSocket   │
│  :5173   │    │   (FastAPI)  │    │  (FastAPI)   │
└──────────┘    └──────┬───────┘    └──────┬───────┘
                      │                    │
                      └────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │PostgreSQL│    │  Redis   │    │  MinIO   │
        │+ pgvector│    │          │    │ (S3 API) │
        └──────────┘    └──────────┘    └──────────┘
                ▲              ▲
                │              │
        ┌───────┴──────────────┴───────┐
        │        arq Workers           │
        │  - Переиндексация эмбеддингов │
        │  - Очистка старых данных     │
        └──────────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Sentence        │
              │ Transformers    │
              │ (paraphrase-    │
              │ multilingual)   │
              └─────────────────┘
```

### 3.2. Ключевые потоки данных

| Откуда | Куда | Протокол | Назначение |
|--------|------|----------|------------|
| Пользователь | Frontend | HTTPS | Запросы страниц, статика |
| Frontend | Backend | REST API (JSON) | CRUD-операции |
| Frontend | Backend | WebSocket | Realtime чат, уведомления |
| Backend | PostgreSQL | SQL/asyncpg | Транзакционные данные |
| Backend | PostgreSQL | pgvector | Семантический поиск |
| Backend | Redis | RESP | Кэш, pub/sub, очереди arq |
| Backend | MinIO | S3 API | Загрузка/скачивание файлов |
| arq Worker | Sentence Transformers | HTTP | Генерация эмбеддингов |
| arq Worker | PostgreSQL | SQL/asyncpg | Обновление эмбеддингов |

---

## 4. Стек технологий

### 4.1. Backend

| Технология | Версия | Обоснование |
|------------|--------|-------------|
| **Python** | 3.13 | Актуальная версия, PEP 703, 684, широкая ML-экосистема |
| **FastAPI** | 0.115+ | Async/await, автогенерация OpenAPI, Pydantic v2 |
| **SQLAlchemy** | 2.0 | Async через asyncpg, typed API (Mapped), зрелая ORM |
| **Alembic** | 1.14+ | Миграции SQLAlchemy |
| **PostgreSQL** | 16 | Надёжная СУБД, JSONB, массивы, ENUM'ы |
| **pgvector** | 0.7+ | Векторное расширение для семантического поиска |
| **Redis** | 7 | Кэш, pub/sub, очереди arq |
| **arq** | 0.26+ | Async-native очередь задач |
| **JWT** | python-jose | Stateless аутентификация, refresh rotation |
| **WebSocket** | через FastAPI | Realtime без дополнительных зависимостей |

### 4.2. Frontend

| Технология | Версия | Обоснование |
|------------|--------|-------------|
| **React** | 19 | React Compiler, огромная экосистема |
| **TypeScript** | 5.6+ | Типобезопасность, автокомплит |
| **Vite** | 6+ | HMR, быстрый production build |
| **Tailwind CSS** | 3.4 | Utility-first CSS |
| **TanStack Query** | 5.60 | Server state, кэширование |
| **Zustand** | 5.0 | Легковесный client state |
| **React Hook Form** | 7.54 | Производительные формы |
| **Zod** | 3.23 | Runtime-валидация |
| **Axios** | 1.7+ | HTTP-клиент, interceptors |

### 4.3. ML / Рекомендательная система

| Технология | Версия | Обоснование |
|------------|--------|-------------|
| **Sentence Transformers** | 3.3+ | Готовая библиотека эмбеддингов |
| **paraphrase-multilingual-MiniLM-L12-v2** | — | 50+ языков (включая русский), размерность 384 |
| **scikit-learn** | 1.5+ | Jaccard similarity, нормализация |
| **pgvector HNSW** | — | Быстрый векторный поиск на стороне БД |

### 4.4. Storage & Infrastructure

| Технология | Версия | Обоснование |
|------------|--------|-------------|
| **MinIO** | 7.2+ | S3-compatible, self-hosted, presigned URLs |
| **Docker Compose** | — | Воспроизводимое окружение |
| **Nginx** | — | Reverse proxy, SSL termination |
| **GitHub Actions** | — | CI/CD, бесплатный tier |
| **pytest + httpx** | — | Backend тесты (unit + integration) |
| **Vitest + RTL** | — | Frontend тесты |
| **SQLAdmin** | 0.16+ | Async админ-панель из SQLAlchemy моделей |

---

## 5. Архитектура Backend

### 5.1. Слоистая архитектура

```
┌─────────────────────────────────────────────────────────────┐
│  API Layer (app/api/)                                       │
│  - HTTP endpoints, WebSocket handlers                       │
│  - Pydantic-схемы для валидации запросов/ответов            │
│  - Dependency Injection (Depends)                            │
│  - Тонкие контроллеры, никакой бизнес-логики                │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Service Layer (app/services/)                              │
│  - Бизнес-логика                                            │
│  - Оркестрация репозиториев и ML                            │
│  - Транзакции, бизнес-правила                               │
│  - Генерация событий (уведомления, очереди)                 │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Repository Layer (app/repositories/)                       │
│  - CRUD-операции через SQLAlchemy async                     │
│  - Сложные запросы (векторный поиск, JOIN)                  │
│  - Инкапсуляция ORM-деталей                                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  ML Layer (app/ml/)                                         │
│  - Embedder (singleton Sentence Transformer)                │
│  - Vector Store (pgvector операции)                         │
│  - Scoring Pipeline (semantic + tech_stack + experience)   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Database (PostgreSQL 16 + pgvector)                        │
└─────────────────────────────────────────────────────────────┘
```

### 5.2. Структура backend-кода

```
backend/
├── app/
│   ├── main.py                  # FastAPI factory, middleware
│   │
│   ├── core/                    # Ядро приложения
│   │   ├── config.py            # pydantic-settings
│   │   ├── database.py          # async engine, sessionmaker
│   │   ├── security.py          # JWT, bcrypt, token rotation
│   │   ├── deps.py              # get_db, get_current_user, get_admin
│   │   ├── exceptions.py        # AppException, NotFoundException, ...
│   │   ├── redis.py             # Redis client, pub/sub
│   │   ├── ws_manager.py        # ConnectionManager, NotificationManager
│   │   ├── minio_client.py      # Presigned URLs
│   │   └── logging.py           # Structured logging setup
│   │
│   ├── models/                  # SQLAlchemy ORM модели
│   │   ├── base.py              # DeclarativeBase, TimestampMixin
│   │   ├── user.py              # User (с skills association_proxy)
│   │   ├── skill.py             # Skill + UserSkill (many-to-many)
│   │   ├── project.py           # Project (с embedding vector(384))
│   │   ├── project_member.py    # Участники команды проекта
│   │   ├── swipe.py             # Swipe (like/pass)
│   │   ├── match.py             # Match (status: active/closed/completed)
│   │   ├── message.py           # Message (chat)
│   │   ├── notification.py      # Notification (JSONB payload)
│   │   ├── refresh_token.py     # JWT refresh с family_id
│   │   └── file.py              # MinIO метаданные
│   │
│   ├── schemas/                 # Pydantic DTO
│   │   ├── auth.py              # LoginRequest, TokenResponse
│   │   ├── user.py              # UserResponse, UserUpdate
│   │   ├── project.py           # ProjectCreate, ProjectResponse
│   │   ├── swipe.py             # SwipeCreate, SwipeReview
│   │   ├── match.py             # MatchResponse
│   │   ├── message.py           # MessageResponse, WSMessageIn/Out
│   │   ├── notification.py      # NotificationResponse
│   │   └── file.py              # FileUploadResponse, FileDownloadResponse
│   │
│   ├── api/                     # HTTP/WebSocket роутеры
│   │   ├── router.py            # Главный агрегатор
│   │   ├── auth.py              # /auth/*
│   │   ├── users.py             # /users/*
│   │   ├── projects.py          # /projects/*
│   │   ├── swipes.py            # /swipes/*
│   │   ├── matches.py           # /matches/*
│   │   ├── chat.py              # /chat/* + /ws/chat/*
│   │   ├── feed.py              # /feed (рекомендации)
│   │   ├── notifications.py     # /notifications + /ws/notifications
│   │   ├── files.py             # /files/*
│   │   └── ws_chat.py           # WebSocket handler чата
│   │
│   ├── services/                # Бизнес-логика
│   │   ├── auth.py              # register, login, refresh, logout
│   │   ├── user.py              # profile management, skills
│   │   ├── project.py           # CRUD, status transitions
│   │   ├── swipe.py             # create, review, inbox
│   │   ├── match.py             # create on approve, close
│   │   ├── chat.py              # save_message, history
│   │   ├── notification.py      # create, push via WS
│   │   ├── file.py              # upload, download (presigned)
│   │   └── recommendation.py    # feed generation, scoring
│   │
│   ├── repositories/            # DAL
│   │   ├── base.py              # Generic CRUD
│   │   ├── user.py
│   │   ├── skill.py             # find_or_create (race-safe)
│   │   ├── project.py           # + vector search
│   │   ├── swipe.py
│   │   ├── match.py             # + is_participant
│   │   ├── message.py           # + count_unread (без OOM)
│   │   ├── notification.py
│   │   ├── project_member.py
│   │   └── refresh_token.py    # get_by_hash, revoke_by_family
│   │
│   ├── ml/                      # ML-подсистема
│   │   ├── embedder.py          # Singleton SentenceTransformer
│   │   ├── text_builder.py      # Профиль/проект → текст для эмбеддинга
│   │   ├── vector_store.py      # pgvector HNSW search
│   │   ├── matching.py          # Scoring pipeline
│   │   └── pipeline.py          # Полный pipeline: text → embed → rank
│   │
│   ├── workers/                 # Фоновые задачи (arq)
│   │   ├── settings.py          # arq WorkerSettings
│   │   └── tasks.py             # reindex_embedding, cleanup_swipes
│   │
│   └── utils/
│       ├── pagination.py        # cursor + offset
│       └── validators.py        # URL, GitHub URL, etc.
│
├── alembic/                     # Миграции БД
├── tests/
│   ├── conftest.py              # Fixtures (db, client, user)
│   ├── factories.py             # factory-boy фабрики
│   ├── unit/                    # services, ml, utils
│   └── integration/             # API endpoints
├── pyproject.toml
└── Dockerfile
```

### 5.3. Dependency Injection

```python
# app/core/deps.py — упрощённый фрагмент

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_token(token, expected_type="access")
    except ValueError:
        raise UnauthorizedException("Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")
    
    user_repo = UserRepository(db)
    user = await user_repo.get(int(user_id))
    
    if user is None:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("User inactive")
    if user.is_banned:
        raise UnauthorizedException("User banned")
    
    return user


def get_swipe_service(db: AsyncSession = Depends(get_db)) -> SwipeService:
    return SwipeService(
        swipe_repo=SwipeRepository(db),
        project_repo=ProjectRepository(db),
        match_repo=MatchRepository(db),
        notification_service=NotificationService(db),
    )
```

---

## 6. Архитектура Frontend

### 6.1. Структура

```
frontend/src/
├── main.tsx                 # Entry point
├── App.tsx                  # Router + Providers
│
├── api/                     # API-клиент
│   ├── client.ts            # Axios + interceptors (token refresh)
│   ├── auth.ts
│   ├── projects.ts
│   ├── swipes.ts
│   ├── matches.ts
│   ├── chat.ts
│   ├── feed.ts
│   └── types.ts             # DTO types
│
├── hooks/                   # Custom hooks
│   ├── useAuth.ts
│   ├── useFeed.ts           # Бесконечная прокрутка
│   ├── useSwipe.ts           # Optimistic updates
│   ├── useChat.ts            # WebSocket + REST fallback
│   └── useNotifications.ts   # WS + unread count
│
├── stores/                  # Zustand
│   ├── authStore.ts         # user, token, isAuthenticated
│   └── uiStore.ts           # theme, sidebar
│
├── components/
│   ├── ui/                  # Базовые (Button, Input, Modal)
│   ├── layout/              # AppLayout, Header, Sidebar
│   ├── feed/                # FeedCard, SwipeButtons, MatchScore
│   ├── matches/             # MatchList, MatchPopup
│   ├── chat/                # ChatWindow, MessageList, MessageInput
│   └── notifications/       # NotificationBell, NotificationList
│
├── pages/                   # Route components
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── FeedPage.tsx
│   ├── MatchesPage.tsx
│   ├── ChatPage.tsx
│   ├── InboxPage.tsx
│   └── ProfilePage.tsx
│
├── router/
│   └── index.tsx            # createBrowserRouter, ProtectedRoute
│
└── utils/
    ├── cn.ts                # clsx + tailwind-merge
    └── formatDate.ts
```

### 6.2. Управление состоянием

| Тип | Инструмент | Пример |
|-----|------------|--------|
| Server state | TanStack Query | Лента проектов, матчи, чат |
| Client state | Zustand | Auth user, UI theme |
| Form state | React Hook Form + Zod | Форма регистрации, профиля |
| URL state | React Router | Параметры пагинации, активный чат |

### 6.3. Axios interceptor для refresh token

```typescript
// frontend/src/api/client.ts (фрагмент)

axiosInstance.interceptors.response.use(
  response => response,
  async error => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refreshToken = useAuthStore.getState().refreshToken;
        const response = await axios.post('/auth/refresh', {
          refresh_token: refreshToken,
        });
        useAuthStore.getState().setTokens(
          response.data.access_token,
          response.data.refresh_token,
        );
        original.headers.Authorization = `Bearer ${response.data.access_token}`;
        return axiosInstance(original);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
```

---

## 7. ML Pipeline

### 7.1. Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│              1. TEXT PREPARATION                            │
│  Developer: name + bio + skills + experience_years          │
│  Project: title + description + requirements + tech_stack  │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              2. EMBEDDING GENERATION                        │
│  SentenceTransformer(paraphrase-multilingual-MiniLM-L12-v2)│
│  → vector(384), L2-normalized                            │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              3. VECTOR STORAGE                             │
│  PostgreSQL + pgvector                                     │
│  HNSW index (m=16, ef_construction=64)                     │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              4. SEMANTIC SEARCH                            │
│  SELECT projects                                          │
│  WHERE status='open' AND owner_id != $user                  │
│    AND NOT EXISTS (swipes)                                 │
│  ORDER BY embedding <=> $dev_embedding LIMIT 50            │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              5. MULTI-FACTOR SCORING                        │
│  score = semantic × 0.6                                    │
│        + tech_stack_match × 0.2                            │
│        + experience_relevance × 0.2                        │
│  (опционально: location × 0.1 — post-MVP)                 │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              6. RANKING & RESPONSE                         │
│  Top-N проектов, отсортированных по score DESC             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2. Формирование текста для эмбеддинга

```python
# app/ml/text_builder.py

def build_developer_text(user: User) -> str:
    """Собрать текстовое представление профиля для эмбеддинга."""
    parts = []
    if user.full_name:
        parts.append(user.full_name)
    if user.bio:
        parts.append(user.bio)
    if user.skills:
        skills_names = [s.name for s in user.skills]
        parts.append("Навыки: " + ", ".join(skills_names))
    if user.experience_years:
        parts.append(f"Опыт: {user.experience_years} лет")
    return ". ".join(parts)


def build_project_text(project: Project) -> str:
    """Собрать текстовое представление проекта для эмбеддинга."""
    parts = [project.title]
    if project.description:
        parts.append(project.description)
    if project.tech_stack:
        tech_names = [s.name for s in project.skills]
        parts.append("Стек: " + ", ".join(tech_names))
    return ". ".join(parts)
```

### 7.3. Embedder — Singleton

```python
# app/ml/embedder.py

from functools import lru_cache
from sentence_transformers import SentenceTransformer
from app.core.config import settings


class Embedder:
    """Singleton-обёртка над SentenceTransformer.
    
    Модель загружается ОДИН раз при старте процесса.
    Занимает ~470 МБ RAM.
    """
    
    def __init__(self):
        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL,
            device=settings.EMBEDDING_DEVICE,
        )
        self.dimension = settings.EMBEDDING_DIM  # 384
    
    def encode(self, texts: list[str]) -> list[list[float]]:
        """Генерация эмбеддингов батчем."""
        embeddings = self.model.encode(
            texts,
            batch_size=settings.EMBEDDING_BATCH_SIZE,
            convert_to_numpy=True,
            normalize_embeddings=True,  # L2 для cosine similarity
        )
        return embeddings.tolist()
    
    def encode_single(self, text: str) -> list[float]:
        return self.encode([text])[0]


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    return Embedder()
```

### 7.4. Scoring

```python
# app/ml/matching.py

def calculate_match_score(
    developer: User,
    project: Project,
    developer_embedding: list[float],
    project_embedding: list[float],
) -> float:
    """Multi-factor scoring."""
    # 1. Семантическое сходство (cosine similarity)
    semantic = cosine_similarity(
        [developer_embedding],
        [project_embedding],
    )[0][0]
    
    # 2. Совпадение технологического стека (Jaccard)
    dev_skills = {s.name.lower() for s in developer.skills}
    proj_skills = {s.name.lower() for s in project.skills}
    tech_stack = len(dev_skills & proj_skills) / len(dev_skills | proj_skills) if (dev_skills | proj_skills) else 0
    
    # 3. Релевантность опыта
    experience = min(developer.experience_years / 5, 1.0)
    
    # 4. Итоговый score
    final = semantic * 0.6 + tech_stack * 0.2 + experience * 0.2
    
    return round(final, 3)
```

### 7.5. Производительность

| Операция | Время |
|----------|-------|
| Загрузка модели при старте | ~10-15 сек |
| Encoding одного текста (CPU) | ~50-100 мс |
| Batch из 32 текстов | ~200-400 мс |
| HNSW vector search (top-50) | ~10-30 мс |
| Полный pipeline `/feed` | ~200-500 мс |

---

## 8. Realtime-коммуникации

### 8.1. Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│  Client A (User 1)            Client B (User 2)             │
│      │                              │                      │
│      │ WS                            │ WS                  │
│      └──────────────┬───────────────┘                      │
│                     │                                      │
│                     ▼                                      │
│        ┌────────────────────────┐                         │
│        │ FastAPI WebSocket      │                         │
│        │ /ws/chat/{match_id}    │                         │
│        └────────────┬───────────┘                         │
│                     │                                      │
│                     ▼                                      │
│        ┌────────────────────────┐                         │
│        │ ConnectionManager       │                         │
│        │ match_id → {user_id → ws}                         │
│        │ (in-memory, per worker)│                         │
│        └────────────┬───────────┘                         │
│                     │                                      │
│                     ▼                                      │
│        ┌────────────────────────┐                         │
│        │ PostgreSQL             │                         │
│        │ messages (persist)     │                         │
│        └────────────────────────┘                         │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  NotificationManager (per user)                        │ │
│  │  /ws/notifications                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  [Future: Redis Pub/Sub для синхронизации                 │
│   между несколькими воркерами backend]                     │
└─────────────────────────────────────────────────────────────┘
```

### 8.2. WebSocket Protocol

#### Chat (`/ws/chat/{match_id}?token=<jwt>`)

**Подключение:**
```
ws://host/ws/chat/{match_id}?token=<access_token>
```

**Отправка (client → server):**
```json
{ "type": "message", "content": "Привет!" }
```

**Получение (server → client):**
```json
{
  "id": 42,
  "match_id": 7,
  "sender_id": 3,
  "content": "Привет!",
  "created_at": "2026-06-24T10:15:30Z"
}
```

**Коды закрытия:**
- `4001` — Неавторизован (нет токена / не access / юзер не найден / забанен)
- `4003` — Нет доступа к матчу
- `4004` — Матч не найден
- `1011` — Внутренняя ошибка

#### Notifications (`/ws/notifications?token=<jwt>`)

```json
// Server → Client
{
  "type": "new_swipe",
  "title": "Новый отклик",
  "payload": {
    "swipe_id": 42,
    "developer_name": "Иван",
    "project_title": "AI чат-бот"
  }
}
```

### 8.3. ConnectionManager

```python
# app/core/ws_manager.py (фрагмент)

class ConnectionManager:
    """Управление WS-соединениями по матчам.
    
    Хранит активные соединения в памяти процесса.
    При нескольких воркерах — потребуется Redis pub/sub.
    """
    
    def __init__(self):
        self._connections: dict[int, dict[int, WebSocket]] = {}
    
    async def connect(self, match_id: int, user_id: int, ws: WebSocket) -> None:
        self._connections.setdefault(match_id, {})[user_id] = ws
    
    def disconnect(self, match_id: int, user_id: int) -> None:
        self._connections.get(match_id, {}).pop(user_id, None)
        if not self._connections.get(match_id):
            self._connections.pop(match_id, None)
    
    async def broadcast(
        self,
        match_id: int,
        data: dict,
        exclude_user_id: int | None = None,
    ) -> None:
        """Разослать сообщение всем участникам матча (кроме exclude)."""
        dead: list[int] = []
        for uid, ws in list(self._connections.get(match_id, {}).items()):
            if uid == exclude_user_id:
                continue
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(uid)
        for uid in dead:
            self.disconnect(match_id, uid)


ws_manager = ConnectionManager()
notification_manager = NotificationManager()
```

---

## 9. Архитектура данных

### 9.1. ER-диаграмма

```
┌─────────────────────────────────────────────────────────────┐
│                          USERS                              │
├─────────────────────────────────────────────────────────────┤
│ PK  id                  BIGSERIAL                           │
│ UQ  email               VARCHAR(255)                        │
│     password_hash       VARCHAR(255)  (bcrypt)              │
│     role                VARCHAR(20)   (user/admin)           │
│     full_name           VARCHAR(150)                        │
│     bio                 TEXT                                │
│     github_url          VARCHAR(255)                        │
│     linkedin_url        VARCHAR(255)                        │
│     portfolio_url       VARCHAR(255)                        │
│     experience_years    SMALLINT     (0-50, CHECK)         │
│ FK  avatar_file_id      → files.id                          │
│ FK  resume_file_id      → files.id                          │
│     embedding           vector(384)                         │
│     is_active           BOOLEAN                             │
│     is_banned           BOOLEAN                             │
│     last_login_at       TIMESTAMPTZ                         │
│     created_at          TIMESTAMPTZ                         │
│     updated_at          TIMESTAMPTZ                         │
│     CHECK (experience_years BETWEEN 0 AND 50)              │
└─────────────────────────────────────────────────────────────┘
        │       │       │       │       │       │
        │ 1:N   │ 1:N   │ 1:N   │ 1:N   │ 1:N   │ 1:N
        ▼       ▼       ▼       ▼       ▼       ▼
   ┌─────────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
   │ user_   │ │files│ │swip│ │mat-│ │mes-│ │noti│
   │ skills  │ │    │ │es  │ │ches│ │sgs │ │fic.│
   └─────────┘ └────┘ └────┘ └────┘ └────┘ └────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│      skills      │    │ project_skills   │    │ project_members  │
├──────────────────┤    ├──────────────────┤    ├──────────────────┤
│ PK id            │    │ PK,FK project_id │    │ PK id            │
│ UQ name          │    │ PK,FK skill_id   │    │ FK project_id    │
└──────────────────┘    └──────────────────┘    │ FK user_id       │
                                                   │ role             │
┌──────────────────┐                             │ is_active        │
│     projects     │                             │ UNIQUE(prj,user) │
├──────────────────┤                             └──────────────────┘
│ PK id            │
│ FK owner_id→user│    ┌──────────────────┐    ┌──────────────────┐
│ title           │    │      swipes      │    │   matches        │
│ description     │    ├──────────────────┤    ├──────────────────┤
│ format          │    │ PK id            │    │ PK id            │
│ payment_type    │    │ FK user_id       │    │ FK user_id       │
│ status          │    │ FK project_id    │    │ FK project_id    │
│ embedding(384)  │    │ message          │    │ FK swipe_id UQ   │
│ created_at      │    │ status           │    │ status           │
│ updated_at      │    │ UNIQUE(user,prj) │    │ UNIQUE(user,prj) │
└──────────────────┘    └──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│     messages     │    │  refresh_tokens  │    │     files        │
├──────────────────┤    ├──────────────────┤    ├──────────────────┤
│ PK id            │    │ PK id            │    │ PK id            │
│ FK match_id      │    │ FK user_id       │    │ FK owner_id      │
│ FK sender_id     │    │ token_hash UQ    │    │ filename         │
│ content          │    │ family_id (UUID) │    │ original_name    │
│ is_read          │    │ expires_at       │    │ path (MinIO key) │
│ read_at          │    │ revoked          │    │ size_bytes       │
│ created_at      │    │ created_at       │    │ mime_type        │
│ CHECK(len 1..4000│    └──────────────────┘    │ bucket           │
└──────────────────┘                              │ is_public        │
                                                   └──────────────────┘
```

### 9.2. Стратегия хранения

| Данные | Хранилище | Обоснование |
|--------|-----------|-------------|
| Пользователи, профили | PostgreSQL | Транзакционность, связи |
| Проекты, свайпы, матчи | PostgreSQL | Транзакционность, ACID |
| Эмбеддинги | PostgreSQL + pgvector | Совместный поиск с фильтрами |
| Навыки | PostgreSQL (нормализация) | Дедидупликация, статистика |
| Сессии WS | In-memory (per worker) | Скорость, локальность |
| Кэш рекомендаций | Redis (TTL 5 мин) | Уменьшение нагрузки на БД |
| Pub/Sub | Redis | Realtime-уведомления |
| Очереди задач | Redis (arq) | Надёжная очередь |
| Файлы | MinIO | S3-compatible, presigned URLs |

### 9.3. Ключевые индексы

```sql
-- Векторные (HNSW для cosine similarity)
CREATE INDEX idx_users_embedding ON users USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_projects_embedding ON projects USING hnsw (embedding vector_cosine_ops);

-- Hot paths (частичные индексы)
CREATE INDEX idx_swipes_project_pending ON swipes(project_id, created_at DESC)
    WHERE status = 'pending';
CREATE INDEX idx_notifications_unread ON notifications(user_id, created_at DESC)
    WHERE is_read = FALSE;

-- Полнотекстовый поиск
CREATE INDEX idx_projects_title_trgm ON projects USING gin(title gin_trgm_ops);

-- Навыки (many-to-many)
CREATE INDEX idx_user_skills_skill ON user_skills(skill_id);
CREATE INDEX idx_project_skills_skill ON project_skills(skill_id);
```

### 9.4. Refresh Token Rotation

```
1. POST /auth/login
   → Создать access (30 мин) + refresh (7 дней)
   → Сохранить refresh_hash + family_id в БД
   → Вернуть оба токена клиенту

2. POST /auth/refresh {refresh_token}
   → Найти по hash в БД
   → Проверить: not revoked, not expired
   → ОТОЗВАТЬ старый (revoked=TRUE)
   → Создать новый с ТЕМ ЖЕ family_id
   → Вернуть новую пару

3. Если в семье обнаружен revoked token (reuse):
   → ОТОЗВАТЬ ВСЮ СЕМЬЮ (все tokens с этим family_id)
   → Логировать как подозрительную активность

4. POST /auth/logout {refresh_token}
   → ОТОЗВАТЬ token (revoked=TRUE)
```

---

## 10. API

### 10.1. REST Endpoints

```
AUTHENTICATION
POST   /auth/register          Регистрация
POST   /auth/login             Логин → access + refresh
POST   /auth/refresh           Обновление пары токенов
POST   /auth/logout            Отзыв refresh token

USERS
GET    /me                     Текущий пользователь
PATCH  /me                     Обновить профиль
PUT    /me/skills               Заменить навыки пользователя
GET    /users/{id}             Публичный профиль

PROJECTS
GET    /projects               Список проектов (публичный)
POST   /projects               Создать проект (требует auth)
GET    /projects/{id}          Детали проекта
PATCH  /projects/{id}          Обновить проект (только владелец)
DELETE /projects/{id}          Удалить проект (только владелец)

FEED & SWIPES
GET    /feed                   Лента рекомендаций (требует auth)
POST   /swipes                 Создать свайп (like)
GET    /swipes/inbox           Входящие отклики (для владельца)
PATCH  /swipes/{id}/review     Одобрить/отклонить

MATCHES
GET    /matches                Список матчей
GET    /matches/{id}           Детали матча
DELETE /matches/{id}           Закрыть матч

CHAT
GET    /chat/{match_id}/messages  История сообщений (cursor-based)

NOTIFICATIONS
GET    /notifications          Список уведомлений
PATCH  /notifications/{id}/read   Отметить прочитанным

FILES
POST   /upload                 Получить presigned URL для загрузки
GET    /files/{id}             Получить presigned URL для скачивания
```

### 10.2. WebSocket Endpoints

```
WS  /ws/chat/{match_id}?token=<jwt>          Realtime чат матча
WS  /ws/notifications?token=<jwt>            Realtime уведомления
```

### 10.3. Формат ответов

```json
// Успех
{
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150
  }
}

// Ошибка
{
  "error": "NOT_FOUND",
  "detail": "Project 42 not found"
}
```

### 10.4. Rate Limiting

| Endpoint | Лимит |
|----------|-------|
| `/auth/login` | 10 req/min per IP |
| `/auth/register` | 5 req/min per IP |
| `/feed` | 60 req/min per user |
| Прочие API | 100 req/min per user |
| WebSocket | 30 msg/sec per connection |

---

## 11. Безопасность

### 11.1. Аутентификация

| Механизм | Описание |
|----------|----------|
| **JWT access token** | TTL 30 минут, передаётся в `Authorization: Bearer` |
| **JWT refresh token** | TTL 7 дней, хранится в БД как SHA-256 hash |
| **family_id rotation** | При refresh — отзыв старого, выдача нового с тем же family |
| **reuse detection** | При использовании revoked token — отзыв всей семьи |

### 11.2. Авторизация

- **Role-based**: `user`, `admin`
- **Resource-based**:
  - Только владелец может редактировать/удалять проект
  - Только участники матча могут читать/писать сообщения
  - Только владелец проекта может одобрять/отклонять свайпы

### 11.3. Защита данных

| Угроза | Мера |
|--------|------|
| SQL injection | SQLAlchemy ORM (параметризованные запросы) |
| XSS | React автоматически экранирует |
| CSRF | SameSite cookies + CORS whitelist |
| Brute-force | Rate limiting на auth endpoints |
| Token theft | Короткий TTL access, refresh rotation |
| File upload attacks | MIME validation, размер ≤ 10 MB |
| Privilege escalation | Проверка прав в каждом сервисе |
| Data leakage | Логи без паролей/токенов, structured logs |

### 11.4. Хеширование паролей

```python
# bcrypt, work factor = 12 (default)
# Длинные пароли (>72 байт) обрезаются bcrypt'ом — пользователь должен 
# быть предупреждён о максимальной длине
```

### 11.5. CORS

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:5173", "https://app.example.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## 12. Масштабируемость и производительность

### 12.1. Целевые метрики (MVP → Production)

| Метрика | MVP | Production |
|---------|-----|------------|
| API latency p95 | < 200 мс | < 100 мс |
| API latency p99 | < 500 мс | < 200 мс |
| WebSocket latency | < 1 с | < 500 мс |
| Feed generation | < 1 с | < 500 мс |
| Concurrent users | 1 000 | 10 000+ |
| Embedding generation | 100 мс | 50 мс |

### 12.2. Стратегия масштабирования

**Horizontal scaling:**
- Backend: stateless → N инстансов за Nginx
- arq Workers: N инстансов, разделяют Redis queue
- WebSocket: **per-worker** ConnectionManager (в MVP)

**Vertical scaling:**
- PostgreSQL: больше CPU/RAM, connection pool (pool_size=10)
- Redis: больше памяти для кэша
- arq Workers: больше CPU для ML

**Caching:**
- Redis cache для `/feed` (TTL 5 мин)
- HTTP cache для статики (Cache-Control headers)
- ML-модель в памяти (singleton)

### 12.3. Оптимизации

**Backend:**
- Async/await везде (FastAPI + SQLAlchemy async)
- Connection pooling (pool_size=10, max_overflow=20)
- Batch-обработка эмбеддингов в arq workers
- Cursor-based пагинация для messages
- `selectinload` для связей (избегаем N+1)

**Frontend:**
- Code splitting (React.lazy)
- TanStack Query cache (5 мин staleTime)
- Virtualization для длинных списков
- Image optimization (lazy loading)

**Database:**
- HNSW индексы для векторного поиска
- Частичные индексы для hot paths
- `trigram` индекс для полнотекстового поиска

---

## 13. Развёртывание

### 13.1. Production Topology

```
┌─────────────────────────────────────────────────────────────┐
│              Load Balancer (Nginx / Cloud LB)              │
│              SSL termination, Rate limiting                │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │Backend 1│        │Backend 2│        │Backend 3│
   │ uvicorn │        │ uvicorn │        │ uvicorn │
   └────┬────┘        └────┬────┘        └────┬────┘
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌──────────┐      ┌──────────┐      ┌──────────┐
   │PostgreSQL│      │  Redis   │      │  MinIO   │
   │+ pgvector│      │ Sentinel │      │ Cluster  │
   └──────────┘      └──────────┘      └──────────┘

   ┌──────────────────────────────────────────────────────┐
   │  arq Workers (2-4 instances)                         │
   │  - reindex_embedding                                │
   │  - cleanup_stale_swipes                             │
   └──────────────────────────────────────────────────────┘

   ┌──────────────────────────────────────────────────────┐
   │  Observability                                       │
   │  - Sentry (errors)                                   │
   │  - Prometheus + Grafana (metrics)                   │
   │  - Loki (logs)                                       │
   └──────────────────────────────────────────────────────┘
```

### 13.2. Docker Compose (production)

```yaml
# docker-compose.prod.yml
services:
  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    environment:
      - APP_ENV=production
    env_file: .env
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G

  worker:
    build: ./backend
    command: arq app.workers.settings.WorkerSettings
    env_file: .env
    depends_on: [db, redis]
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G  # ML-модель

  frontend:
    build: ./frontend
    restart: unless-stopped

  db:
    image: pgvector/pgvector:pg16
    volumes: [pgdata:/var/lib/postgresql/data]
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 10s

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes: [redisdata:/data]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    volumes: [miniodata:/data]

  nginx:
    build: ./nginx
    ports: ["80:80", "443:443"]
    depends_on: [backend, frontend]
    volumes:
      - certbot-conf:/etc/letsencrypt
      - certbot-www:/var/www/certbot

volumes:
  pgdata: {}
  redisdata: {}
  miniodata: {}
  certbot-conf: {}
  certbot-www: {}
```

### 13.3. CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run backend tests
        run: |
          docker compose up -d db redis minio
          docker compose run backend pytest --cov=app --cov-fail-under=80
      - name: Run frontend tests
        run: |
          cd frontend
          npm ci
          npm run type-check
          npm run lint
          npm run test
```

---

## 14. Сквозные сценарии

### 14.1. Сценарий: Свайп → Матч → Чат

```
DEVELOPER                FRONTEND              BACKEND                 DB                  OWNER
    │                       │                    │                     │                   │
    │ 1. GET /feed          │                    │                     │                   │
    │──────────────────────▶│                    │                     │                   │
    │                       │ GET /feed          │                     │                   │
    │                       │───────────────────▶│                     │                   │
    │                       │                    │ 1.1 Загрузить профиль│                  │
    │                       │                    │────────────────────▶│                   │
    │                       │                    │ 1.2 Получить embedding                 │
    │                       │                    │ 1.3 Vector search  │                   │
    │                       │                    │────────────────────▶│                   │
    │                       │                    │ 1.4 Scoring         │                   │
    │                       │                    │ 1.5 Top-20 проектов │                   │
    │                       │ feed[]             │                     │                   │
    │                       │◀───────────────────│                     │                   │
    │ feed[]                │                    │                     │                   │
    │◀──────────────────────│                    │                     │                   │
    │                       │                    │                     │                   │
    │ 2. POST /swipes {like}│                    │                     │                   │
    │──────────────────────▶│                    │                     │                   │
    │                       │ POST /swipes       │                     │                   │
    │                       │───────────────────▶│                     │                   │
    │                       │                    │ 2.1 Проверить UNIQUE│                   │
    │                       │                    │ 2.2 INSERT swipe   │                   │
    │                       │                    │────────────────────▶│                   │
    │                       │                    │ 2.3 NOTIFY owner   │                   │
    │                       │                    │────────────────────▶│                   │
    │                       │ 201 Created        │                     │                   │
    │                       │◀───────────────────│                     │                   │
    │                       │                    │                     │                   │
    │                       │                    │ 3. WS notification │                   │
    │                       │                    │─────────────────────────────────────────▶│
    │                       │                    │                     │ "new_swipe"        │
    │                       │                    │                     │                   │
    │                       │                    │ 4. PATCH /swipes/{id}/review {approve}  │
    │                       │                    │◀────────────────────────────────────────│
    │                       │                    │ 4.1 UPDATE swipe.status                  │
    │                       │                    │────────────────────▶│                   │
    │                       │                    │ 4.2 INSERT match    │                   │
    │                       │                    │────────────────────▶│                   │
    │                       │                    │ 4.3 NOTIFY обеим    │                   │
    │                       │                    │────────────────────▶│                   │
    │                       │                    │                     │                   │
    │ 5. WS "It's a Match!" │                    │                     │                   │
    │◀──────────────────────│                    │                     │                   │
    │                       │                    │ 5. WS "It's a Match!"                   │
    │                       │                    │─────────────────────────────────────────▶│
    │                       │                    │                     │                   │
    │ 6. WS message "Привет"│                    │                     │                   │
    │──────────────────────▶│                    │                     │                   │
    │                       │ WS /ws/chat/42     │                     │                   │
    │                       │───────────────────▶│                     │                   │
    │                       │                    │ 6.1 Проверить is_participant            │
    │                       │                    │ 6.2 INSERT message  │                   │
    │                       │                    │────────────────────▶│                   │
    │                       │                    │ 6.3 Broadcast (exclude sender)         │
    │                       │                    │─────────────────────────────────────────▶│
    │                       │                    │                     │ 7. WS "Привет!"   │
```

### 14.2. Сценарий: Обновление профиля → Переиндексация

```
USER                  BACKEND                  arq Worker              ML Model
  │                       │                          │                       │
  │ PATCH /me             │                          │                       │
  │──────────────────────▶│                          │                       │
  │                       │ 1. UPDATE user           │                       │
  │                       │                          │                       │
  │                       │ 2. ENQUEUE reindex_user  │                       │
  │                       │─────────────────────────▶│                       │
  │                       │                          │                       │
  │                       │ 200 OK                   │                       │
  │◀──────────────────────│                          │                       │
  │ profile updated       │                          │                       │
  │                       │                          │                       │
  │                       │                          │ 3. LOAD user          │
  │                       │                          │──────────────────────▶│
  │                       │                          │ 4. BUILD text         │
  │                       │                          │──────────────────────▶│
  │                       │                          │                       │
  │                       │                          │ 5. ENCODE             │
  │                       │                          │──────────────────────▶│
  │                       │                          │◀──────────────────────│
  │                       │                          │ embedding             │
  │                       │                          │                       │
  │                       │                          │ 6. UPDATE user.embedding
  │                       │                          │ 7. HNSW auto-update   │
```

---

## Приложения

### A. Переменные окружения (.env)

```bash
# App
APP_ENV=production
SECRET_KEY=<openssl rand -hex 32>
API_URL=https://api.example.com
FRONTEND_URL=https://app.example.com

# Database
POSTGRES_USER=tinder_app
POSTGRES_PASSWORD=<strong_password>
POSTGRES_DB=tinder_devs
DATABASE_URL=postgresql+asyncpg://tinder_app:password@db:5432/tinder_devs

# Redis
REDIS_PASSWORD=<strong_password>
REDIS_URL=redis://:password@redis:6379/0

# JWT
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_EXTERNAL_ENDPOINT=cdn.example.com
MINIO_ACCESS_KEY=<access_key>
MINIO_SECRET_KEY=<secret_key>
MINIO_BUCKET=uploads
MINIO_USE_SSL=true

# ML
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIM=384
EMBEDDING_BATCH_SIZE=32
EMBEDDING_DEVICE=cpu

# CORS
CORS_ORIGINS=["https://app.example.com"]

# Logging
LOG_LEVEL=INFO

# Sentry
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### B. Полезные команды (Makefile)

```makefile
.PHONY: up down logs migrate test seed lint deploy

up:
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

down:
    docker compose down

logs:
    docker compose logs -f $(service)

migrate:
    docker compose exec backend alembic upgrade head

migrate-create:
    docker compose exec backend alembic revision --autogenerate -m "$(msg)"

test:
    docker compose exec backend pytest -v
    cd frontend && npm run test

seed:
    docker compose exec backend python scripts/seed.py

embed:
    docker compose exec backend python scripts/embed_all.py

lint:
    docker compose exec backend ruff check .
    cd frontend && npm run lint

deploy:
    ./scripts/deploy.sh
```
### 15. Изменения в архитектуре: Слой быстрого доступа (Caching Layer)
Для снижения нагрузки на реляционную СУБД в систему внедрен Redis. 

1. **Кэширование сессий:** Данные авторизации OAuth не запрашивают основную БД при каждом действии пользователя.
2. **Очередь свайпов:** Поток "лайков" сначала аккумулируется в оперативной памяти (Redis), после чего фоновый воркер (Background Worker) пачками сбрасывает их в PostgreSQL. Это предотвращает блокировку таблиц при высокой интенсивности приложения.

