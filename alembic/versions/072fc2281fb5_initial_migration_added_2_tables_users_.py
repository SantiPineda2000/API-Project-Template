"""Initial migration, added 2 Tables Users and Roles.

Revision ID: 072fc2281fb5
Revises: 
Create Date: 2024-11-06 13:22:25.118047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '072fc2281fb5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('date_created', sa.Date(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('first_name', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('last_name', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('birthday', sa.Date(), nullable=False),
    sa.Column('phone_number', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('register_date', sa.Date(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('terminated_at', sa.Date(), nullable=True),
    sa.Column('img_path', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('user_name', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('is_owner', sa.Boolean(), nullable=True),
    sa.Column('salary', sa.Float(), nullable=False),
    sa.Column('roles_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['roles_id'], ['roles.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('roles')
    # ### end Alembic commands ###
