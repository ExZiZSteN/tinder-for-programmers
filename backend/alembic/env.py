# backend/alembic/env.py

"""Alembic environment configuration.

Подключается к БД через настройки из app.core.config.
Импортирует все модели из app.models для autogenerate.
"""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
import pgvector
import pgvector.sqlalchemy

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Импортируем настройки и модели
from app.core.config import settings
from app.models.base import Base  # DeclarativeBase
from app.models.user import User  # все модели для autogenerate
from app.models.skill import Skill
from app.models.user_skill import UserSkill
from app.models.project import Project
from app.models.project_skill import ProjectSkill
from app.models.project_member import ProjectMember
from app.models.swipe import Swipe
from app.models.match import Match
from app.models.message import Message
from app.models.notification import Notification
from app.models.refresh_token import RefreshToken
from app.models.file import File
from app.models.project_message import ProjectMessage

# Конфиг Alembic
config = context.config

# Подставляем URL из настроек (важно — не хранить в alembic.ini)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в offline-режиме (без подключения к БД).
    
    Генерирует SQL-скрипты, не подключаясь к БД.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Основная логика миграций (синхронная)."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Запуск миграций в online-режиме (async)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций в online-режиме."""
    asyncio.run(run_async_migrations())


# Определяем режим
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
