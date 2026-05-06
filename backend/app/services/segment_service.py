import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.segment import TranscriptSegment
from app.services.audio.vad import SpeechSegment


async def create_segments_from_vad(
    db: AsyncSession,
    meeting_id: uuid.UUID,
    audio_file_id: uuid.UUID,
    speech_segments: list[SpeechSegment],
) -> list[TranscriptSegment]:
    segments = [
        TranscriptSegment(
            meeting_id=meeting_id,
            audio_file_id=audio_file_id,
            segment_index=i,
            start_ms=seg.start_ms,
            end_ms=seg.end_ms,
        )
        for i, seg in enumerate(speech_segments)
    ]
    db.add_all(segments)
    await db.commit()
    for seg in segments:
        await db.refresh(seg)
    return segments


async def list_segments_for_meeting(
    db: AsyncSession,
    meeting_id: uuid.UUID,
) -> list[TranscriptSegment]:
    result = await db.execute(
        select(TranscriptSegment)
        .where(TranscriptSegment.meeting_id == meeting_id)
        .order_by(TranscriptSegment.segment_index)
    )
    return list(result.scalars().all())


async def get_segment(
    db: AsyncSession,
    segment_id: uuid.UUID,
) -> TranscriptSegment | None:
    result = await db.execute(
        select(TranscriptSegment).where(TranscriptSegment.id == segment_id)
    )
    return result.scalar_one_or_none()


async def update_segment(
    db: AsyncSession,
    segment: TranscriptSegment,
    corrected_text: str | None,
    speaker_label: str | None,
) -> TranscriptSegment:
    if corrected_text is not None:
        segment.corrected_text = corrected_text
    if speaker_label is not None:
        segment.speaker_label = speaker_label
    await db.commit()
    await db.refresh(segment)
    return segment
