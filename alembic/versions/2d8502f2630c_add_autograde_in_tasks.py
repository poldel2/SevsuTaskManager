from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2d8502f2630c'
down_revision: Union[str, None] = 'df4286c5e42f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Создаём ENUM типы вручную перед использованием
    taskgrade = postgresql.ENUM('EASY', 'MEDIUM', 'HARD', name='taskgrade', create_type=True)
    taskstatus = postgresql.ENUM('TODO', 'IN_PROGRESS', 'DONE', 'REVIEW', name='taskstatus', create_type=True)
    taskpriority = postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', name='taskpriority', create_type=True)

    # Применяем типы к таблицам
    taskgrade.create(op.get_bind(), checkfirst=True)
    taskstatus.create(op.get_bind(), checkfirst=True)
    taskpriority.create(op.get_bind(), checkfirst=True)

    # Создаём таблицы и изменяем колонки
    op.create_table('project_grading_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('required_easy_tasks', sa.Integer(), nullable=True),
        sa.Column('required_medium_tasks', sa.Integer(), nullable=True),
        sa.Column('required_hard_tasks', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id')
    )

    op.create_table('user_project_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('completed_easy', sa.Integer(), nullable=True),
        sa.Column('completed_medium', sa.Integer(), nullable=True),
        sa.Column('completed_hard', sa.Integer(), nullable=True),
        sa.Column('auto_grade', sa.String(length=20), nullable=True),
        sa.Column('manual_grade', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.add_column('tasks', sa.Column('grade', taskgrade, nullable=True))
    op.alter_column('tasks', 'status',
           existing_type=sa.VARCHAR(length=20),
           type_=taskstatus,
           postgresql_using="status::taskstatus",
           existing_nullable=True)
    op.alter_column('tasks', 'priority',
           existing_type=sa.VARCHAR(length=10),
           type_=taskpriority,
           postgresql_using="priority::taskpriority",
           existing_nullable=True)

def downgrade() -> None:
    # Удаляем колонки и таблицы
    op.drop_column('tasks', 'grade')
    op.alter_column('tasks', 'priority',
           existing_type=sa.Enum('LOW', 'MEDIUM', 'HIGH', name='taskpriority'),
           type_=sa.VARCHAR(length=10),
           existing_nullable=True)
    op.alter_column('tasks', 'status',
           existing_type=sa.Enum('TODO', 'IN_PROGRESS', 'DONE', 'REVIEW', name='taskstatus'),
           type_=sa.VARCHAR(length=20),
           existing_nullable=True)
    op.drop_table('user_project_progress')
    op.drop_table('project_grading_settings')

    # Удаляем ENUM типы
    op.execute('DROP TYPE IF EXISTS taskgrade')
    op.execute('DROP TYPE IF EXISTS taskstatus')
    op.execute('DROP TYPE IF EXISTS taskpriority')
