"""Add due_date in tasks

Revision ID: df4286c5e42f
Revises: 77a592ad2eb5
Create Date: 2025-03-22 16:08:56.385609

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df4286c5e42f'
down_revision: Union[str, None] = '77a592ad2eb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'due_date')
    # ### end Alembic commands ###
