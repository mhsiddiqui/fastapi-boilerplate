"""auto migration

Revision ID: 3c8e20ebf595
Revises:
Create Date: 2024-10-21 11:39:40.720382

"""
from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3c8e20ebf595"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "token_blacklist", ["id"])
    op.create_unique_constraint(None, "user", ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "user", type_="unique")
    op.drop_constraint(None, "token_blacklist", type_="unique")
    # ### end Alembic commands ###
