"""views_count for arts

Revision ID: 1ca96e142bb2
Revises: bd98bab39111
Create Date: 2024-09-29 13:32:51.924519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '1ca96e142bb2'
down_revision: Union[str, None] = 'bd98bab39111'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('arts', sa.Column('views_count', sa.Integer(), server_default=sa.text('0'),
                                    nullable=False))


def downgrade() -> None:
    op.drop_column('arts', 'views_count')
