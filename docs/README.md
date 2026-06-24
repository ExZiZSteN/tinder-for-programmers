# Документация проекта

## Tinder for Programmers

## Содержание

### Для начала работы
- [Быстрый старт](./getting-started.md) — как развернуть проект локально
- [Руководство разработчика](./development.md) — структура кода, соглашения, workflow

### Архитектура
- [Архитектура системы](./architecture.md) — TDD, компоненты, потоки данных
- [Схема БД](./database.md) — ER-диаграмма, таблицы, индексы
- [ML Pipeline](./ml-pipeline.md) — рекомендательная система
- [Realtime](./realtime.md) — WebSocket, чат, уведомления

### API и интеграции
- [API Reference](./api.md) — REST и WebSocket endpoints

### Эксплуатация
- [Развёртывание](./deployment.md) — production-деплой
- [Тестирование](./testing.md) — unit, integration, e2e
- [Troubleshooting](./troubleshooting.md) — частые проблемы

### Контрибуция
- [Contributing](./contributing.md) — как внести свой вклад

## Кому читать что

| Роль | Что читать |
|------|------------|
| Новый разработчик | getting-started → development → architecture |
| Frontend-разработчик | api → realtime → development |
| Backend-разработчик | database → ml-pipeline → api → testing |
| ML-инженер | ml-pipeline → database |
| DevOps | deployment → testing |
| QA | testing → api → troubleshooting |