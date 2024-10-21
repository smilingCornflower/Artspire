"""cascade delete

Revision ID: fc8882024dd5
Revises: 1ca96e142bb2
Create Date: 2024-10-19 21:44:22.834775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fc8882024dd5'
down_revision: Union[str, None] = '1ca96e142bb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('fk_users_to_likes_art_id_arts', 'users_to_likes', type_='foreignkey')
    op.create_foreign_key(op.f('fk_users_to_likes_art_id_arts'), 'users_to_likes', 'arts',
                          ['art_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_users_to_saves_art_id_arts', 'users_to_saves', type_='foreignkey')
    op.create_foreign_key(op.f('fk_users_to_saves_art_id_arts'), 'users_to_saves', 'arts',
                          ['art_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint(op.f('fk_users_to_saves_art_id_arts'), 'users_to_saves', type_='foreignkey')
    op.create_foreign_key('fk_users_to_saves_art_id_arts', 'users_to_saves', 'arts', ['art_id'],
                          ['id'])
    op.drop_constraint(op.f('fk_users_to_likes_art_id_arts'), 'users_to_likes', type_='foreignkey')
    op.create_foreign_key('fk_users_to_likes_art_id_arts', 'users_to_likes', 'arts', ['art_id'],
                          ['id'])
