import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.export_record import ExportRecord
from app.models.meeting import Meeting
from app.models.segment import TranscriptSegment
from app.models.summary import MeetingSummary
from app.services.export import summary_exporter, transcript_exporter


async def export_transcript(
    db: AsyncSession, meeting: Meeting, file_format: str
) -> ExportRecord:
    segs_result = await db.execute(
        select(TranscriptSegment)
        .where(TranscriptSegment.meeting_id == meeting.id)
        .order_by(TranscriptSegment.segment_index)
    )
    segments = list(segs_result.scalars().all())

    if file_format == "md":
        path = transcript_exporter.export_md(meeting, segments, settings.export_storage_path)
    else:
        path = transcript_exporter.export_docx(meeting, segments, settings.export_storage_path)

    record = ExportRecord(
        meeting_id=meeting.id,
        export_type="transcript",
        file_format=file_format,
        file_path=path,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def export_summary(
    db: AsyncSession, summary: MeetingSummary, file_format: str
) -> ExportRecord:
    meeting_result = await db.execute(
        select(Meeting).where(Meeting.id == summary.meeting_id)
    )
    meeting = meeting_result.scalar_one()

    if file_format == "md":
        path = summary_exporter.export_md(meeting, summary, settings.export_storage_path)
    else:
        path = summary_exporter.export_docx(meeting, summary, settings.export_storage_path)

    record = ExportRecord(
        meeting_id=meeting.id,
        summary_id=summary.id,
        export_type="summary",
        file_format=file_format,
        file_path=path,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_export_record(
    db: AsyncSession, export_id: uuid.UUID
) -> ExportRecord | None:
    result = await db.execute(
        select(ExportRecord).where(ExportRecord.id == export_id)
    )
    return result.scalar_one_or_none()
