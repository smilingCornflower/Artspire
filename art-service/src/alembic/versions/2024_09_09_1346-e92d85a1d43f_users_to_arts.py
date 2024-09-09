"""users_to_arts

Revision ID: e92d85a1d43f
Revises: 86edc6e3fb94
Create Date: 2024-09-09 13:46:37.022279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e92d85a1d43f'
down_revision: Union[str, None] = '86edc6e3fb94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users_to_saves',
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('art_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['art_id'], ['arts.id'],
                                            name=op.f('fk_users_to_saves_art_id_arts')),
                    sa.PrimaryKeyConstraint('user_id', 'art_id', name=op.f('pk_users_to_saves'))
                    )


def downgrade() -> None:
    op.drop_table('users_to_saves')
