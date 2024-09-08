"""user_saved

Revision ID: 3ba4e1d443fe
Revises: 86edc6e3fb94
Create Date: 2024-09-08 16:05:11.288910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3ba4e1d443fe'
down_revision: Union[str, None] = '86edc6e3fb94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user_saved_arts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('arts', sa.ARRAY(sa.Integer()), nullable=True),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_saved_arts'))
                    )
    op.create_index(op.f('ix_user_saved_arts_id'), 'user_saved_arts', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_saved_arts_id'), table_name='user_saved_arts')
    op.drop_table('user_saved_arts')
