"""transcript_segments table

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transcript_segments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "meeting_id",
            UUID(as_uuid=True),
            sa.ForeignKey("meetings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "audio_file_id",
            UUID(as_uuid=True),
            sa.ForeignKey("audio_files.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("segment_index", sa.Integer, nullable=False),
        sa.Column("start_ms", sa.Integer, nullable=False),
        sa.Column("end_ms", sa.Integer, nullable=False),
        sa.Column("speaker_label", sa.String(100)),
        sa.Column("raw_text", sa.Text),
        sa.Column("corrected_text", sa.Text),
        sa.Column("confidence", sa.Numeric(5, 4)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_transcript_segments_meeting_id", "transcript_segments", ["meeting_id"])


def downgrade() -> None:
    op.drop_table("transcript_segments")
