"""empty message

Revision ID: 5e17ef77f31c
Revises: 4beab9064488
Create Date: 2017-10-24 18:13:31.670229

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5e17ef77f31c'
down_revision = '4beab9064488'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('vendor', 'min_income')
    op.drop_column('vendor', 'min_price')
    op.drop_column('vendor', 'max_income')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vendor', sa.Column('max_income', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('vendor', sa.Column('min_price', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('vendor', sa.Column('min_income', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
