# Тестирование

##  Уровни тестирования

| Уровень | Инструменты | Покрытие |
|---------|-------------|----------|
| Unit | pytest | services, ml, utils |
| Integration | pytest + httpx | API endpoints |
| Frontend | Vitest + RTL | hooks, components |
| E2E | Playwright (опционально) | критические user flows |

##  Backend-тесты

### Запуск

```bash
# Все тесты
make test

# Только unit
docker compose exec backend pytest tests/unit -v

# Только integration
docker compose exec backend pytest tests/integration -v

# С coverage
docker compose exec backend pytest --cov=app --cov-report=html
```

### Структура тестов

```
tests/
├── conftest.py          # Общие fixtures
├── factories.py         # factory-boy фабрики
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

### Примеры

#### Unit-тест для ML

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

#### Integration-тест для API

```python
# tests/integration/test_swipes.py
async def test_create_swipe(client, user, project):
    # Arrange
    token = await get_token(client, user)
    
    # Act
    response = await client.post(
        '/swipes',
        json={'project_id': project.id},
        headers={'Authorization': f'Bearer {token}'}
    )
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data['status'] == 'pending'

async def test_cannot_swipe_own_project(client, owner, own_project):
    token = await get_token(client, owner)
    response = await client.post(
        '/swipes',
        json={'project_id': own_project.id},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 403
```

### Fixtures

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url='http://test') as client:
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

##  Frontend-тесты

### Запуск

```bash
docker compose exec frontend npm run test
```

### Пример

```typescript
// components/feed/__tests__/FeedCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { FeedCard } from '../FeedCard';

test('calls onLike when like button clicked', () => {
  const onLike = vi.fn();
  render(<FeedCard project={mockProject} onLike={onLike} onPass={() => {}} />);
  
  fireEvent.click(screen.getByRole('button', { name: /like/i }));
  
  expect(onLike).toHaveBeenCalled();
});
```

##  Coverage

Целевое покрытие: **> 80%**

```bash
# Отчёт
docker compose exec backend pytest --cov=app --cov-report=term-missing
```

##  CI/CD

GitHub Actions автоматически запускает тесты на каждый PR:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          docker compose up -d db redis
          docker compose run backend pytest --cov=app
```