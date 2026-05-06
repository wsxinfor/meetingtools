import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.schemas.term import TermCreate, TermOut, TermUpdate
from app.services import meeting_service, term_service

router = APIRouter(tags=["terms"])


@router.get("/terms", response_model=dict)
async def list_terms(
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    terms = await term_service.list_terms(db)
    return {"code": 0, "data": [TermOut.model_validate(t).model_dump() for t in terms], "msg": "ok"}


@router.post("/terms", response_model=dict)
async def create_term(
    data: TermCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    term = await term_service.create_term(db, data)
    return {"code": 0, "data": TermOut.model_validate(term).model_dump(), "msg": "ok"}


@router.put("/terms/{term_id}", response_model=dict)
async def update_term(
    term_id: uuid.UUID,
    data: TermUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    term = await term_service.get_term(db, term_id)
    if not term:
        raise HTTPException(status_code=404, detail="术语不存在")
    term = await term_service.update_term(db, term, data)
    return {"code": 0, "data": TermOut.model_validate(term).model_dump(), "msg": "ok"}


@router.delete("/terms/{term_id}", response_model=dict)
async def delete_term(
    term_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    term = await term_service.get_term(db, term_id)
    if not term:
        raise HTTPException(status_code=404, detail="术语不存在")
    await term_service.delete_term(db, term)
    return {"code": 0, "data": None, "msg": "ok"}


@router.post("/meetings/{meeting_id}/apply-terms", response_model=dict)
async def apply_terms(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    if current_user.role != "admin" and meeting.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="会议不存在")
    corrected_text, segments_updated = await term_service.apply_terms_to_meeting(db, meeting)
    return {
        "code": 0,
        "data": {"corrected_text": corrected_text, "segments_updated": segments_updated},
        "msg": "ok",
    }
