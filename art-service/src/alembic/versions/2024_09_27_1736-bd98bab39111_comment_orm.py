"""comment orm

Revision ID: bd98bab39111
Revises: 5ca18cd171f2
Create Date: 2024-09-27 17:36:46.224291

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bd98bab39111'
down_revision: Union[str, None] = '5ca18cd171f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('comments',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('art_id', sa.Integer(), nullable=False),
                    sa.Column('text', sa.String(length=512), nullable=False),
                    sa.Column('likes_count', sa.Integer(), nullable=False),
                    sa.Column('dislikes_count', sa.Integer(), nullable=False),
                    sa.Column('is_edited', sa.Boolean(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.ForeignKeyConstraint(['art_id'], ['arts.id'],
                                            name=op.f('fk_comments_art_id_arts')),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_comments'))
                    )


def downgrade() -> None:
    op.drop_table('comments')
