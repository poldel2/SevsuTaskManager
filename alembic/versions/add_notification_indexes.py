"""add_notification_indexes

Revision ID: xxx
Revises: 1d2b5fd3002b
Create Date: 2025-04-09 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'xxx'
down_revision: Union[str, None] = '1d2b5fd3002b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])
    op.create_index('ix_notifications_read', 'notifications', ['read'])

def downgrade() -> None:
    op.drop_index('ix_notifications_read', 'notifications')
    op.drop_index('ix_notifications_created_at', 'notifications')