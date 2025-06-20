"""Update task model and schema add start_date


Revision ID: 88a68ee6b85d
Revises: f23c27960a6a
Create Date: 2025-03-31 17:05:31.930808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88a68ee6b85d'
down_revision: Union[str, None] = 'f23c27960a6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('start_date', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'start_date')
    # ### end Alembic commands ###
