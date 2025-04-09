import pytest
import pytest_asyncio
from sqlalchemy import select
from models.domain.users import User
from models.domain.projects import Project
from models.domain.tasks import Task
from models.domain.sprints import Sprint
from models.domain.messages import Message
from models.domain.user_project import user_project_table, Role
from models.domain.grading import ProjectGradingSettings, UserProjectProgress
from .test_data import (
    TEST_USER_DATA,
    TEST_PROJECT_DATA,
    TEST_SPRINT_DATA,
    TEST_TASK_DATA,
    TEST_MESSAGE_DATA,
    TEST_PROGRESS_DATA,
    TEST_GRADING_SETTINGS_DATA
)

@pytest_asyncio.fixture
async def test_user(db_session):
    """Создает тестового пользователя в БД"""
    user = User(
        id=TEST_USER_DATA["id"],
        sub=TEST_USER_DATA["sub"],
        email=TEST_USER_DATA["email"],
        first_name=TEST_USER_DATA["first_name"],
        last_name=TEST_USER_DATA["last_name"]
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_project(db_session, test_user):
    """Создает тестовый проект в БД"""
    project = Project(**TEST_PROJECT_DATA)
    db_session.add(project)
    
    # Добавляем связь пользователь-проект
    await db_session.execute(
        user_project_table.insert().values(
            user_id=test_user.id,
            project_id=project.id,
            role=Role.ADMIN
        )
    )
    
    await db_session.commit()
    await db_session.refresh(project)
    return project

@pytest_asyncio.fixture
async def test_sprint(db_session, test_project):
    """Создает тестовый спринт в БД"""
    sprint = Sprint(**TEST_SPRINT_DATA)
    db_session.add(sprint)
    await db_session.commit()
    await db_session.refresh(sprint)
    return sprint

@pytest_asyncio.fixture
async def test_task(db_session, test_project, test_user, test_sprint):
    """Создает тестовую задачу в БД"""
    task = Task(**TEST_TASK_DATA)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task

@pytest_asyncio.fixture
async def test_grading_settings(db_session, test_project):
    """Создает тестовые настройки оценивания в БД"""
    settings = ProjectGradingSettings(**TEST_GRADING_SETTINGS_DATA)
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)
    return settings

@pytest_asyncio.fixture
async def test_progress(db_session, test_project, test_user):
    """Создает тестовый прогресс пользователя в БД"""
    progress = UserProjectProgress(**TEST_PROGRESS_DATA)
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)
    return progress

@pytest_asyncio.fixture
async def test_message(db_session, test_project, test_user):
    """Создает тестовое сообщение в БД"""
    message = Message(**TEST_MESSAGE_DATA)
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return message