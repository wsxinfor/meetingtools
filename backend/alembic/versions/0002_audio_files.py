"""audio_files table

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-29

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audio_files",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "meeting_id",
            UUID(as_uuid=True),
            sa.ForeignKey("meetings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("normalized_path", sa.String(1000)),
        sa.Column("file_size", sa.Integer),
        sa.Column("duration_seconds", sa.Numeric(10, 2)),
        sa.Column("sample_rate", sa.Integer),
        sa.Column("channels", sa.Integer),
        sa.Column("status", sa.String(50), nullable=False, server_default="uploaded"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_audio_files_meeting_id", "audio_files", ["meeting_id"])


def downgrade() -> None:
    op.drop_table("audio_files")
