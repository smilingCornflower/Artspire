"""followings and followers into user

Revision ID: 694e7bc2475e
Revises: aea0ed2233f8
Create Date: 2024-10-28 23:20:16.171015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '694e7bc2475e'
down_revision: Union[str, None] = 'aea0ed2233f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column(
        'followers_count', sa.Integer(), server_default=sa.text('0'), nullable=False))
    op.add_column('users', sa.Column(
        'followings_count', sa.Integer(), server_default=sa.text('0'), nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'followings_count')
    op.drop_column('users', 'followers_count')
