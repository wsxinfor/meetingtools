import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import Meeting
from app.models.segment import TranscriptSegment
from app.models.term import TermDictionary
from app.schemas.term import TermCreate, TermUpdate


async def create_term(db: AsyncSession, data: TermCreate) -> TermDictionary:
    term = TermDictionary(**data.model_dump())
    db.add(term)
    await db.commit()
    await db.refresh(term)
    return term


async def list_terms(db: AsyncSession) -> list[TermDictionary]:
    result = await db.execute(select(TermDictionary).order_by(TermDictionary.created_at))
    return list(result.scalars().all())


async def get_term(db: AsyncSession, term_id: uuid.UUID) -> TermDictionary | None:
    result = await db.execute(select(TermDictionary).where(TermDictionary.id == term_id))
    return result.scalar_one_or_none()


async def update_term(db: AsyncSession, term: TermDictionary, data: TermUpdate) -> TermDictionary:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(term, field, value)
    await db.commit()
    await db.refresh(term)
    return term


async def delete_term(db: AsyncSession, term: TermDictionary) -> None:
    await db.delete(term)
    await db.commit()


async def apply_terms_to_meeting(
    db: AsyncSession,
    meeting: Meeting,
) -> tuple[str, int]:
    """Apply all enabled terms to meeting raw_text → corrected_text and to each segment.

    Returns (corrected_text, segments_updated).
    """
    result = await db.execute(
        select(TermDictionary)
        .where(TermDictionary.enabled.is_(True))
        .order_by(TermDictionary.created_at)
    )
    terms = list(result.scalars().all())

    # Build ordered replacement pairs: (wrong, correct)
    pairs: list[tuple[str, str]] = []
    for t in terms:
        pairs.append((t.wrong_text, t.correct_text))
        for alias in (t.aliases or []):
            pairs.append((alias, t.correct_text))

    source = meeting.raw_text or ""
    corrected = _apply_replacements(source, pairs)

    meeting.corrected_text = corrected
    await db.flush()

    # Apply to each segment
    segs_result = await db.execute(
        select(TranscriptSegment)
        .where(TranscriptSegment.meeting_id == meeting.id)
        .order_by(TranscriptSegment.segment_index)
    )
    segments = list(segs_result.scalars().all())
    updated = 0
    for seg in segments:
        seg_source = seg.raw_text or ""
        seg.corrected_text = _apply_replacements(seg_source, pairs)
        updated += 1

    await db.commit()
    return corrected, updated


def _apply_replacements(text: str, pairs: list[tuple[str, str]]) -> str:
    for wrong, correct in pairs:
        if wrong:
            text = text.replace(wrong, correct)
    return text
