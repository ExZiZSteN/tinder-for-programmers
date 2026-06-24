# Contributing


##  Как начать

1. Форкнуть репозиторий
2. Создать ветку от `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
3. Внести изменения
4. Написать/обновить тесты
5. Проверить lint:
   ```bash
   make lint
   make test
   ```
6. Закоммитить в формате conventional commits:
   ```bash
   git commit -m "feat(swipe): add animation on like"
   ```
7. Push и создать Pull Request

## 📝 Conventional Commits

Формат: `<type>(<scope>): <description>`

**Types:**
- `feat` — новая функциональность
- `fix` — исправление бага
- `docs` — документация
- `style` — форматирование (не влияет на код)
- `refactor` — рефакторинг
- `test` — тесты
- `chore` — инфраструктура, зависимости

**Примеры:**
```
feat(auth): add OAuth login
fix(chat): fix message ordering
docs(api): update endpoints description
refactor(ml): extract scoring pipeline
```

##  Стиль кода

### Python
- Line length: 100
- Type hints обязательны
- Docstrings в Google-style для публичных API
- Formatter: ruff

### TypeScript
- Strict mode
- Formatter: Prettier
- Lint: ESLint


