# ML Pipeline — Рекомендательная система

## Назначение

Рекомендательная система формирует персонализированную ленту проектов для разработчика на основе семантического сходства между профилем пользователя и требованиями проекта.

---

# Используемая модель

| Параметр | Значение |
|----------|-----------|
| **Модель** | `paraphrase-multilingual-MiniLM-L12-v2` |
| **Размерность эмбеддинга** | `384` |
| **Поддерживаемые языки** | 50+ (включая русский и английский) |
| **Размер модели** | ~470 МБ |

## Почему выбрана именно эта модель

- Поддерживает русский язык.
- Обеспечивает хорошее качество поиска при небольшом размере.
- Размерность **384** оптимально подходит для `pgvector`.

---

# Pipeline

```text
┌─────────────────────────────────────────────────────────────┐
│  1. TEXT PREPARATION                                        │
│                                                             │
│  Developer: name + bio + skills + experience                │
│  Project: title + description + requirements + tech_stack   │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  2. EMBEDDING GENERATION                                    │
│                                                             │
│  Sentence Transformers → vector(384)                        │
│  L2-normalized для cosine similarity                        │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  3. VECTOR STORAGE                                          │
│                                                             │
│  PostgreSQL + pgvector                                      │
│  HNSW index (m=16, ef_construction=64)                      │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  4. SEMANTIC SEARCH                                         │
│                                                             │
│  SELECT ... ORDER BY embedding <=> $dev_embedding           │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  5. MULTI-FACTOR SCORING                                    │
│                                                             │
│  score = semantic × 0.6                                     │
│        + tech_stack × 0.2                                   │
│        + experience × 0.2                                   │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  6. RANKING & RESPONSE                                      │
│                                                             │
│  Top-20 проектов, отсортированных по score                  │
└─────────────────────────────────────────────────────────────┘
```

---

# Формирование текста

## Для разработчика

```python
def build_developer_text(user) -> str:
    parts = []

    if user.full_name:
        parts.append(user.full_name)

    if user.bio:
        parts.append(user.bio)

    if user.skills:
        parts.append(
            "Навыки: " + ", ".join(s.name for s in user.skills)
        )

    if user.experience_years:
        parts.append(
            f"Опыт: {user.experience_years} лет"
        )

    return ". ".join(parts)
```

### Пример результата

```text
Иван Иванов.

Backend-разработчик с опытом в высоконагруженных системах.

Навыки:
Python, FastAPI, PostgreSQL, Redis, Docker.

Опыт: 5 лет.
```

---

## Для проекта

```python
def build_project_text(project) -> str:
    parts = [project.title]

    if project.description:
        parts.append(project.description)

    if project.requirements:
        parts.append(
            "Требования: " + ", ".join(project.requirements)
        )

    if project.tech_stack:
        parts.append(
            "Стек: " + ", ".join(s.name for s in project.skills)
        )

    return ". ".join(parts)
```

---

# Формула скоринга

```text
final_score =
    semantic × 0.6
  + techStack × 0.2
  + experience × 0.2
```

## Где

```text
semantic_similarity =
    1 - cosine_distance(dev_emb, proj_emb)

Диапазон: 0..1
```

```text
techStack =
    Jaccard similarity между навыками разработчика
    и стеком проекта
```

```text
experience =
    min(experience_years / 5, 1.0)
```

---

## Пример расчёта

```text
semantic    = 0.85
techStack   = 0.70
experience  = 0.80   (4 года)

final_score =
0.85 × 0.6 +
0.70 × 0.2 +
0.80 × 0.2

= 0.81
```

---

# Переиндексация

Обновление эмбеддингов происходит асинхронно через **arq**.

```text
Пользователь обновляет профиль
            │
            ▼
POST /users/me
            │
            ▼
Service
            │
            ▼
Сохранение в БД
            │
            ▼
Постановка задачи:
reindex_developer(user_id)
            │
            ▼
arq Worker
            │
            ▼
Загрузка профиля
            │
            ▼
Генерация embedding
            │
            ▼
Обновление БД
            │
            ▼
Автоматическое обновление HNSW-индекса
```

---

# Производительность

| Операция | Время |
|-----------|-------:|
| Загрузка модели при старте | ~10–15 сек |
| Инференс одного текста | ~50–100 мс |
| Batch из 32 текстов | ~200–400 мс |
| Vector Search (Top-50) | ~10–30 мс |
| Полный pipeline `/feed` | ~200–500 мс |

---

# Конфигурация

```bash
# .env

EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIM=384
EMBEDDING_BATCH_SIZE=32
EMBEDDING_DEVICE=cpu   # либо cuda при наличии GPU
```

---

# Тестирование

```python
# tests/unit/test_embedder.py

def test_embedding_dimension():
    embedder = get_embedder()

    emb = embedder.encode_single(
        "Python developer"
    )

    assert len(emb) == 384


def test_multilingual():
    embedder = get_embedder()

    ru = embedder.encode_single(
        "Python разработчик"
    )

    en = embedder.encode_single(
        "Python developer"
    )

    similarity = cosine_similarity([ru], [en])[0][0]

    assert similarity > 0.85
```

---

# Возможные улучшения

- Fine-tuned модель, обученная на домене IT-проектов.
- Collaborative Filtering на основе истории свайпов.
- A/B-тестирование различных формул скоринга.
- Учёт географического положения и часовых поясов пользователей.
