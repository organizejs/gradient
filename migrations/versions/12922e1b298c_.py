"""empty message

Revision ID: 12922e1b298c
Revises: 1bc190da5811
Create Date: 2018-06-09 21:02:44.381133

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12922e1b298c'
down_revision = '1bc190da5811'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('transaction', 'requester_ip')
    op.drop_column('transaction_audit', 'requester_ip')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transaction_audit', sa.Column('requester_ip', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('transaction', sa.Column('requester_ip', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
