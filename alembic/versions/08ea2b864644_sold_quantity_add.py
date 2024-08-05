"""sold_quantity add

Revision ID: 08ea2b864644
Revises: c7924af6bd7c
Create Date: 2024-08-06 03:20:59.208037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08ea2b864644'
down_revision = 'c7924af6bd7c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('sold_quantity', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'sold_quantity')
    # ### end Alembic commands ###