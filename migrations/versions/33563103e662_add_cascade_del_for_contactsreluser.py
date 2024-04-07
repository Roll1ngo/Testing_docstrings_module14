"""add_cascade_del_for_contactsRELuser

Revision ID: 33563103e662
Revises: c120ee42efff
Create Date: 2024-04-04 10:55:31.102630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '33563103e662'
down_revision: Union[str, None] = 'c120ee42efff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('contacts_user_id_fkey', 'contacts', type_='foreignkey')
    op.create_foreign_key(None, 'contacts', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'contacts', type_='foreignkey')
    op.create_foreign_key('contacts_user_id_fkey', 'contacts', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###
