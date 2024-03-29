"""added user to maintenance history

Revision ID: 4d48f145a0b6
Revises: 2afc78cf07e3
Create Date: 2023-07-21 19:33:36.381370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d48f145a0b6'
down_revision = '2afc78cf07e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user', sa.String(length=200), nullable=False, default=''))


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_history', schema=None) as batch_op:
        batch_op.drop_column('user')

    # ### end Alembic commands ###
