import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingDetailOut, MeetingOut, MeetingUpdate, SpeakerMapUpdate
from app.services import meeting_service

router = APIRouter(prefix="/meetings", tags=["meetings"])


def _check_meeting_access(meeting, current_user: User) -> None:
    """Raise 404 if non-admin user doesn't own the meeting."""
    if current_user.role != "admin" and meeting.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="会议不存在")


@router.post("", response_model=dict)
async def create_meeting(
    data: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.create_meeting(db, data, owner_id=current_user.id)
    return {"code": 0, "data": MeetingOut.model_validate(meeting).model_dump(), "msg": "ok"}


@router.get("", response_model=dict)
async def list_meetings(
    keyword: str | None = Query(None),
    customer_id: uuid.UUID | None = Query(None),
    project_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    owner_filter = None if current_user.role == "admin" else current_user.id
    total, items = await meeting_service.list_meetings(
        db, keyword, customer_id, project_id, status, page, page_size, owner_id=owner_filter
    )
    return {
        "code": 0,
        "data": {
            "total": total,
            "items": [MeetingOut.model_validate(m).model_dump() for m in items],
        },
        "msg": "ok",
    }


@router.get("/{meeting_id}", response_model=dict)
async def get_meeting(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)
    return {"code": 0, "data": MeetingDetailOut.model_validate(meeting).model_dump(), "msg": "ok"}


@router.put("/{meeting_id}", response_model=dict)
async def update_meeting(
    meeting_id: uuid.UUID,
    data: MeetingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)
    meeting = await meeting_service.update_meeting(db, meeting, data)
    return {"code": 0, "data": MeetingDetailOut.model_validate(meeting).model_dump(), "msg": "ok"}


@router.put("/{meeting_id}/corrected-text", response_model=dict)
async def save_corrected_text(
    meeting_id: uuid.UUID,
    corrected_text: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)
    meeting = await meeting_service.save_corrected_text(db, meeting, corrected_text)
    return {"code": 0, "data": MeetingDetailOut.model_validate(meeting).model_dump(), "msg": "ok"}


@router.patch("/{meeting_id}/speaker-map", response_model=dict)
async def update_speaker_map(
    meeting_id: uuid.UUID,
    data: SpeakerMapUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)
    meeting = await meeting_service.update_speaker_map(db, meeting, data.speaker_map)
    return {"code": 0, "data": MeetingDetailOut.model_validate(meeting).model_dump(), "msg": "ok"}


@router.delete("/{meeting_id}", response_model=dict)
async def delete_meeting(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)
    await meeting_service.delete_meeting(db, meeting)
    return {"code": 0, "data": None, "msg": "ok"}
