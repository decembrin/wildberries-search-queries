"""0005

Revision ID: 11229f2e6858
Revises: a3701d0c5d54
Create Date: 2025-03-04 04:07:50.647339

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from infrastructure.repositories.sqlalchemy_constants import (
    SEARCH_QUERY_DAILY_STATS_TABLE_NAME,
    SEARCH_QUERY_DAILY_STATS_TPL_TABLE_NAME,
)

# revision identifiers, used by Alembic.
revision: str = '11229f2e6858'
down_revision: Union[str, None] = 'a3701d0c5d54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
     op.execute(
        f"SELECT partman.create_parent( "
        f"     p_parent_table := 'public.{SEARCH_QUERY_DAILY_STATS_TABLE_NAME}' "
        f"   , p_control := 'day' "
        f"   , p_interval := '1 month' "
        f"   , p_template_table := 'public.{SEARCH_QUERY_DAILY_STATS_TPL_TABLE_NAME}' "
        f");"
     )


def downgrade() -> None:
    pass
