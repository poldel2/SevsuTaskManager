"""Update task model and schemas for grading


Revision ID: f23c27960a6a
Revises: 12d75c5a0b4c
Create Date: 2025-03-28 11:45:02.603238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f23c27960a6a'
down_revision: Union[str, None] = '12d75c5a0b4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('feedback', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'feedback')
    # ### end Alembic commands ###
