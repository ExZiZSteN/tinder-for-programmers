# Тестирование

## Уровни тестирования

| Уровень | Инструменты | Область покрытия |
|----------|-------------|------------------|
| **Unit** | `pytest` | `services`, `ml`, `utils` |
| **Integration** | `pytest` + `httpx` | API endpoints |
| **Frontend** | `Vitest` + `React Testing Library (RTL)` | `hooks`, `components` |
| **E2E** | `Playwright` *(опционально)* | Критические пользовательские сценарии |

---

# Backend-тесты

## Запуск тестов

```bash
# Запуск всех тестов проекта
make test

# Запуск только модульных тестов
docker compose exec backend pytest tests/unit -v

# Запуск только интеграционных тестов
docker compose exec backend pytest tests/integration -v

# Запуск тестов с отчётом о покрытии
docker compose exec backend pytest --cov=app --cov-report=html
```

---

## Структура директории тестов

```text
tests/
├── conftest.py          # Общие фикстуры (fixtures)
├── factories.py         # Генерация тестовых данных (factory-boy)
├── unit/
│   ├── test_security.py
│   ├── test_matching.py
│   └── test_embedder.py
└── integration/
    ├── test_auth.py
    ├── test_swipes.py
    ├── test_matches.py
    ├── test_chat.py
    └── test_feed.py
```

---

# Примеры реализации

## Unit-тест ML-компонента

```python
# tests/unit/test_embedder.py

def test_embedding_dimension():
    embedder = get_embedder()
    emb = embedder.encode_single("Python developer")

    assert len(emb) == 384


def test_multilingual_similarity():
    embedder = get_embedder()

    ru = embedder.encode_single("Python разработчик")
    en = embedder.encode_single("Python developer")

    similarity = cosine_similarity([ru], [en])[0][0]

    assert similarity > 0.85
```

---

## Интеграционный тест API

```python
# tests/integration/test_swipes.py

async def test_create_swipe(client, user, project):
    # Arrange — подготовка окружения
    token = await get_token(client, user)

    # Act
    response = await client.post(
        "/swipes",
        json={"project_id": project.id},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Assert
    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "pending"


async def test_cannot_swipe_own_project(client, owner, own_project):
    token = await get_token(client, owner)

    response = await client.post(
        "/swipes",
        json={"project_id": own_project.id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
```

---

# Базовые фикстуры (Fixtures)

```python
# tests/conftest.py

import pytest
from httpx import AsyncClient


@pytest.fixture
async def client():
    async with AsyncClient(
        app=app,
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
async def db_session():
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def user(db_session):
    user = UserFactory()

    db_session.add(user)
    await db_session.commit()

    return user
```

---

# Frontend-тесты

## Запуск тестов

```bash
docker compose exec frontend npm run test
```

## Пример теста компонента

```tsx
// components/feed/__tests__/FeedCard.test.tsx

import { render, screen, fireEvent } from "@testing-library/react";
import { FeedCard } from "../FeedCard";

test("calls onLike when like button clicked", () => {
  const onLike = vi.fn();

  render(
    <FeedCard
      project={mockProject}
      onLike={onLike}
      onPass={() => {}}
    />
  );

  fireEvent.click(
    screen.getByRole("button", {
      name: /like/i,
    })
  );

  expect(onLike).toHaveBeenCalled();
});
```

---

# Покрытие кода (Coverage)

Минимальное целевое покрытие для стабильной сборки — **не менее 80%**.

```bash
# Подробный отчёт о непокрытых строках
docker compose exec backend pytest --cov=app --cov-report=term-missing
```

---

# Автоматизация (CI/CD)

Тестовый набор автоматически запускается через **GitHub Actions** при каждом:

- `push`
- `pull_request`

## Пример workflow

```yaml
# .github/workflows/ci.yml

name: CI

on:
  - push
  - pull_request

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run tests inside Docker architecture
        run: |
          docker compose up -d db redis
          docker compose run backend pytest --cov=app
```
