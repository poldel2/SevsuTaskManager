from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import asyncio

# Импорт ваших моделей
from models.domain.users import User
from models.domain.projects import Project
from models.domain.sprints import Sprint
from models.domain.tasks import *
from models.domain.messages import Message
from models.domain.user_project import user_project_table
from models.domain.task_columns import TaskColumn
from models.domain.tokens import Token
from models.domain.notifications import Notification
from models.domain.project_activities import ProjectActivity
from models.domain.reports import Report

config = context.config
target_metadata = user_project_table.metadata

# Настройка логгирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    """Запуск миграций в offline-режиме (без подключения к БД)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Запуск миграций в online-режиме (с подключением к БД)"""
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        future=True
    )

    async def run_async_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    asyncio.run(run_async_migrations())

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()