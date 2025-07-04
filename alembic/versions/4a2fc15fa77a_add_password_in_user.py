"""Add password in user

Revision ID: 4a2fc15fa77a
Revises: ae4630578aea
Create Date: 2025-02-26 11:43:55.493910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a2fc15fa77a'
down_revision: Union[str, None] = 'ae4630578aea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'hashed_password')
    # ### end Alembic commands ###
