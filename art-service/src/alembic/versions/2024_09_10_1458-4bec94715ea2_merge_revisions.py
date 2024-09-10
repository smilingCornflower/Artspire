"""merge revisions

Revision ID: 4bec94715ea2
Revises: 3ba4e1d443fe, e92d85a1d43f
Create Date: 2024-09-10 14:58:24.880556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bec94715ea2'
down_revision: Union[str, None] = ('3ba4e1d443fe', 'e92d85a1d43f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
