"""Add first and last name fields

Revision ID: d290cf6662dd
Revises: a02134dda3fe
Create Date: 2025-02-13 23:16:02.989201

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd290cf6662dd'
down_revision = 'a02134dda3fe'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('first_name', sa.String(length=50), nullable=False, server_default='Unknown'))
        batch_op.add_column(sa.Column('last_name', sa.String(length=50), nullable=False, server_default='Unknown'))


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')

    # ### end Alembic commands ###
