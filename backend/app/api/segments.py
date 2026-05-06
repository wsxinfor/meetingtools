import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.segment import TranscriptSegmentOut, TranscriptSegmentUpdate
from app.services import meeting_service, segment_service

router = APIRouter(tags=["segments"])


def _check_meeting_access(meeting, current_user: User) -> None:
    if current_user.role != "admin" and meeting.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="会议不存在")


@router.get("/meetings/{meeting_id}/transcript-segments", response_model=dict)
async def list_segments(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)
    segments = await segment_service.list_segments_for_meeting(db, meeting_id)
    return {
        "code": 0,
        "data": [TranscriptSegmentOut.model_validate(s).model_dump() for s in segments],
        "msg": "ok",
    }


@router.put("/transcript-segments/{segment_id}", response_model=dict)
async def update_segment(
    segment_id: uuid.UUID,
    body: TranscriptSegmentUpdate,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    segment = await segment_service.get_segment(db, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="片段不存在")
    updated = await segment_service.update_segment(
        db, segment, body.corrected_text, body.speaker_label
    )
    return {"code": 0, "data": TranscriptSegmentOut.model_validate(updated).model_dump(), "msg": "ok"}
