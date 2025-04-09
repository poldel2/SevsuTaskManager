import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from models.domain.user_project import Role
from .test_data import (
    TEST_USER_DATA,
    TEST_PROJECT_DATA,
    TEST_SPRINT_DATA,
    TEST_TASK_DATA,
    TEST_PROGRESS_DATA,
    TEST_GRADING_SETTINGS_DATA
)

@pytest_asyncio.fixture
async def mock_auth_service():
    with AsyncMock() as mock:
        mock.verify_token.return_value = True
        mock.get_current_user.return_value = TEST_USER_DATA
        mock.is_teacher.return_value = TEST_USER_DATA["is_teacher"]
        yield mock

@pytest_asyncio.fixture
async def mock_project_service():
    with AsyncMock() as mock:
        mock.get_project.return_value = TEST_PROJECT_DATA
        mock.get_user_project_role.return_value = Role.ADMIN
        mock.is_project_leader.return_value = True
        mock.has_project_access.return_value = True
        mock.get_project_members.return_value = [TEST_USER_DATA]
        yield mock

@pytest_asyncio.fixture
async def mock_sprint_service():
    with AsyncMock() as mock:
        mock.get_sprint.return_value = TEST_SPRINT_DATA
        mock.get_active_sprint.return_value = TEST_SPRINT_DATA
        mock.get_sprint_tasks.return_value = [TEST_TASK_DATA]
        yield mock

@pytest_asyncio.fixture
async def mock_task_service():
    with AsyncMock() as mock:
        mock.get_task.return_value = TEST_TASK_DATA
        mock.get_project_tasks.return_value = [TEST_TASK_DATA]
        mock.is_task_assignee.return_value = True
        mock.can_manage_task.return_value = True
        yield mock

@pytest_asyncio.fixture
async def mock_grading_service():
    with AsyncMock() as mock:
        mock.get_progress.return_value = TEST_PROGRESS_DATA
        mock.get_grading_settings.return_value = TEST_GRADING_SETTINGS_DATA
        mock.calculate_auto_grade.return_value = "B"
        mock.can_submit_for_review.return_value = True
        mock.can_approve_task.return_value = True
        yield mock

@pytest_asyncio.fixture
async def mock_message_service():
    with AsyncMock() as mock:
        mock.get_project_messages.return_value = []
        mock.can_access_chat.return_value = True
        yield mock