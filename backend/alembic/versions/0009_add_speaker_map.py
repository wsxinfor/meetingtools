"""add speaker_map to meetings

Revision ID: 0009
Revises: 0008
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("meetings", sa.Column("speaker_map", JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("meetings", "speaker_map")
