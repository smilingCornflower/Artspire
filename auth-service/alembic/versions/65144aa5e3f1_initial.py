"""initial

Revision ID: 65144aa5e3f1
Revises: 
Create Date: 2024-08-24 00:18:28.485774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '65144aa5e3f1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('roles',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_roles')),
                    sa.UniqueConstraint('name', name=op.f('uq_roles_name'))
                    )
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username', sa.String(length=50), nullable=False),
                    sa.Column('email', sa.String(length=255), nullable=False),
                    sa.Column('hashed_password', sa.String(length=64), nullable=False),
                    sa.Column('role_id', sa.Integer(), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('is_verified', sa.Boolean(), nullable=False),
                    sa.Column('profile_image', sa.String(length=255), nullable=True),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('fk_users_role_id_roles')),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
                    sa.UniqueConstraint('email', name=op.f('uq_users_email')),
                    sa.UniqueConstraint('username', name=op.f('uq_users_username'))
                    )


def downgrade() -> None:
    op.drop_table('users')
    op.drop_table('roles')
