"""assign tasks to users

Revision ID: 2afc78cf07e3
Revises: e52759549cd6
Create Date: 2023-07-19 17:47:52.834389

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2afc78cf07e3'
down_revision = 'e52759549cd6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.String(length=36), nullable=True))
        batch_op.create_foreign_key('fk_user_id', 'user', ['user_id'], ['id'])


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_task', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###