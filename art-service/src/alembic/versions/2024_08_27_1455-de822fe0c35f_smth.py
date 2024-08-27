"""smth

Revision ID: de822fe0c35f
Revises: 
Create Date: 2024-08-27 14:55:44.197629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'de822fe0c35f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('arts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('url', sa.String(length=512), nullable=False),
                    sa.Column('title', sa.String(length=256), nullable=True),
                    sa.Column('likes_count', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_arts'))
                    )
    op.create_index(op.f('ix_arts_url'), 'arts', ['url'], unique=True)
    op.create_table('tags',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_tags')),
                    sa.UniqueConstraint('name', name=op.f('uq_tags_name'))
                    )
    op.create_table('arts_to_tags',
                    sa.Column('art_id', sa.Integer(), nullable=False),
                    sa.Column('tag_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['art_id'], ['arts.id'], name=op.f('fk_arts_to_tags_art_id_arts'),
                                            ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name=op.f('fk_arts_to_tags_tag_id_tags'),
                                            ondelete='CASCADE')
                    )

def downgrade() -> None:
    op.drop_table('arts_to_tags')
    op.drop_table('tags')
    op.drop_index(op.f('ix_arts_url'), table_name='arts')
    op.drop_table('arts')
