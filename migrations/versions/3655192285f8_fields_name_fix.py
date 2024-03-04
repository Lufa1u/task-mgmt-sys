"""fields name fix

Revision ID: 3655192285f8
Revises: 0c1cf1fe72f0
Create Date: 2024-03-04 20:33:14.920256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3655192285f8'
down_revision: Union[str, None] = '0c1cf1fe72f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('creator_user_id', sa.Integer(), nullable=True))
    op.drop_constraint('tasks_creator_id_fkey', 'tasks', type_='foreignkey')
    op.create_foreign_key(None, 'tasks', 'users', ['creator_user_id'], ['id'])
    op.drop_column('tasks', 'creator_id')
    op.add_column('users', sa.Column('role', sa.Enum('USER', 'MODERATOR', 'ADMIN', name='userroleenummodel'), nullable=False))
    op.drop_index('ix_users_user_role', table_name='users')
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    op.drop_column('users', 'user_role')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('user_role', postgresql.ENUM('USER', 'MODERATOR', 'ADMIN', name='userroleenummodel'), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.create_index('ix_users_user_role', 'users', ['user_role'], unique=False)
    op.drop_column('users', 'role')
    op.add_column('tasks', sa.Column('creator_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.create_foreign_key('tasks_creator_id_fkey', 'tasks', 'users', ['creator_id'], ['id'])
    op.drop_column('tasks', 'creator_user_id')
    # ### end Alembic commands ###