"""empty message

Revision ID: 143ee3e99967
Revises: f8e883e5b327
Create Date: 2018-05-31 19:39:42.462006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '143ee3e99967'
down_revision = 'f8e883e5b327'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gradient_price', sa.Column('quantity', sa.Integer(), nullable=False))
    op.add_column('gradient_price_audit', sa.Column('quantity', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('gradient_price_audit', 'quantity')
    op.drop_column('gradient_price', 'quantity')
    # ### end Alembic commands ###