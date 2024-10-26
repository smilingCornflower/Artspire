"""subscribtions

Revision ID: aea0ed2233f8
Revises: 6268bc8cbe87
Create Date: 2024-10-25 20:47:43.349515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'aea0ed2233f8'
down_revision: Union[str, None] = '6268bc8cbe87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('subscriptions',
                    sa.Column('follower_id', sa.Integer(), nullable=False),
                    sa.Column('artist_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['artist_id'], ['users.id'],
                                            name=op.f('fk_subscriptions_artist_id_users'),
                                            ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['follower_id'], ['users.id'],
                                            name=op.f('fk_subscriptions_follower_id_users'),
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('follower_id', 'artist_id',
                                            name=op.f('pk_subscriptions'))
                    )


def downgrade() -> None:
    op.drop_table('subscriptions')
