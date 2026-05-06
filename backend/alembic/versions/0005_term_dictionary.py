"""term_dictionary table

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "term_dictionary",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("category", sa.String(50), nullable=False, server_default="common"),
        sa.Column("wrong_text", sa.String(500), nullable=False),
        sa.Column("correct_text", sa.String(500), nullable=False),
        sa.Column("aliases", JSONB),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("term_dictionary")
