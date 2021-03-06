"""empty message

Revision ID: 74a15d195fb9
Revises: eb57f17e2522
Create Date: 2017-09-05 16:57:54.127264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74a15d195fb9'
down_revision = 'eb57f17e2522'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('transaction', 'customer_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('transaction', 'customer_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
