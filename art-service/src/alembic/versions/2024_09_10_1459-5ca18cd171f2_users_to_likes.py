"""users to likes

Revision ID: 5ca18cd171f2
Revises: 4bec94715ea2
Create Date: 2024-09-10 14:59:22.954070

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5ca18cd171f2'
down_revision: Union[str, None] = '4bec94715ea2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users_to_likes',
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('art_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['art_id'], ['arts.id'],
                                            name=op.f('fk_users_to_likes_art_id_arts')),
                    sa.PrimaryKeyConstraint('user_id', 'art_id', name=op.f('pk_users_to_likes'))
                    )
    op.drop_index('ix_user_saved_arts_id', table_name='user_saved_arts')
    op.drop_table('user_saved_arts')


def downgrade() -> None:
    op.create_table('user_saved_arts',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('arts', postgresql.ARRAY(sa.INTEGER()), autoincrement=False,
                              nullable=True),
                    sa.PrimaryKeyConstraint('id', name='pk_user_saved_arts')
                    )
    op.create_index('ix_user_saved_arts_id', 'user_saved_arts', ['id'], unique=False)
    op.drop_table('users_to_likes')
