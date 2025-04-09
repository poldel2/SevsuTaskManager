from datetime import datetime, timedelta, timezone
from models.domain.tasks import TaskStatus, TaskPriority, TaskGrade
from models.domain.user_project import Role

TEST_USER_DATA = {
    "id": 1,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "sub": "test-sub",
    "is_teacher": False,
    "project_roles": {1: "ADMIN"}
}

TEST_PROJECT_DATA = {
    "id": 1,
    "title": "Test Project",
    "description": "Test Project Description",
    "start_date": datetime.now(timezone.utc),
    "end_date": datetime.now(timezone.utc) + timedelta(days=30),
    "owner_id": TEST_USER_DATA["id"]
}

TEST_SPRINT_DATA = {
    "id": 1,
    "title": "Test Sprint",
    "description": "Test Sprint Description",
    "start_date": datetime.now(timezone.utc),
    "end_date": datetime.now(timezone.utc) + timedelta(days=14),
    "status": "ACTIVE",
    "project_id": TEST_PROJECT_DATA["id"]
}

TEST_TASK_DATA = {
    "id": 1,
    "title": "Test Task",
    "description": "Test Description",
    "status": TaskStatus.TODO,
    "priority": TaskPriority.MEDIUM,
    "grade": TaskGrade.MEDIUM,
    "feedback": None,
    "created_at": datetime.now(timezone.utc),
    "updated_at": datetime.now(timezone.utc),
    "due_date": datetime.now(timezone.utc) + timedelta(days=7),
    "start_date": datetime.now(timezone.utc),
    "project_id": TEST_PROJECT_DATA["id"],
    "sprint_id": TEST_SPRINT_DATA["id"],
    "assignee_id": TEST_USER_DATA["id"]
}

TEST_TASK_COLUMN_DATA = {
    "id": 1,
    "name": "To Do",
    "project_id": TEST_PROJECT_DATA["id"],
    "position": 1,
    "color": "#ffffff"
}

TEST_MESSAGE_DATA = {
    "id": 1,
    "project_id": TEST_PROJECT_DATA["id"],
    "sender_id": TEST_USER_DATA["id"],
    "content": "Test message content",
    "created_at": datetime.now(timezone.utc)
}

# Данные для разных сценариев тестирования
TEST_TASK_STATUSES = [
    TaskStatus.TODO,
    TaskStatus.IN_PROGRESS,
    TaskStatus.NEED_REVIEW,
    TaskStatus.APPROVED_BY_LEADER,
    TaskStatus.APPROVED_BY_TEACHER,
    TaskStatus.REJECTED
]

TEST_USER_ROLES = [
    Role.OWNER,
    Role.ADMIN,
    Role.MEMBER,
    Role.TEACHER
]

TEST_TASK_PRIORITIES = [
    TaskPriority.LOW,
    TaskPriority.MEDIUM,
    TaskPriority.HIGH
]

TEST_TASK_GRADES = [
    TaskGrade.EASY,
    TaskGrade.MEDIUM,
    TaskGrade.HARD
]

# Данные для тестирования прогресса
TEST_PROGRESS_DATA = {
    "id": 1,
    "user_id": TEST_USER_DATA["id"],
    "project_id": TEST_PROJECT_DATA["id"],
    "completed_easy": 2,
    "completed_medium": 1,
    "completed_hard": 0,
    "created_at": datetime.now(timezone.utc),
    "auto_grade": "B",
    "manual_grade": None
}

# Данные для тестирования настроек оценивания проекта
TEST_GRADING_SETTINGS_DATA = {
    "id": 1,
    "project_id": TEST_PROJECT_DATA["id"],
    "required_easy_tasks": 3,
    "required_medium_tasks": 2,
    "required_hard_tasks": 1
}