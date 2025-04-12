"""add_project_activities_table

Revision ID: 1dd2254e133f
Revises: xxx
Create Date: 2025-04-11 22:16:30.313036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1dd2254e133f'
down_revision: Union[str, None] = 'xxx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('project_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_activities_id'), 'project_activities', ['id'], unique=False)
    op.create_index(op.f('ix_project_activities_project_id'), 'project_activities', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_activities_created_at'), 'project_activities', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_project_activities_created_at'), table_name='project_activities')
    op.drop_index(op.f('ix_project_activities_project_id'), table_name='project_activities')
    op.drop_index(op.f('ix_project_activities_id'), table_name='project_activities')
    op.drop_table('project_activities')
