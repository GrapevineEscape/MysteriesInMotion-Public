"""Add RoleApplication model

Revision ID: bae7d34758e2
Revises: 86348d830270
Create Date: 2025-02-14 00:08:21.762952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bae7d34758e2'
down_revision = '86348d830270'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role_application',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('performer_id', sa.Integer(), nullable=False),
    sa.Column('show_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('applied_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['performer_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['show_id'], ['show.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('role_application')
    # ### end Alembic commands ###
