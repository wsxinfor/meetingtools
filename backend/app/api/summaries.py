import uuid

import openai
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.summary import SummaryCreate, SummaryOut, SummaryUpdate
from app.services import meeting_service, summary_service

router = APIRouter(tags=["summaries"])


def _check_meeting_access(meeting, current_user: User) -> None:
    if current_user.role != "admin" and meeting.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="会议不存在")


@router.post("/meetings/{meeting_id}/summaries", response_model=dict)
async def generate_summary(
    meeting_id: uuid.UUID,
    data: SummaryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)
    try:
        summary = await summary_service.generate_summary(db, meeting, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except openai.APIConnectionError as exc:
        raise HTTPException(status_code=502, detail=f"LLM 连接失败: {exc}") from exc
    except openai.AuthenticationError as exc:
        raise HTTPException(status_code=502, detail="LLM 认证失败，请检查 API Key") from exc
    except openai.RateLimitError as exc:
        raise HTTPException(status_code=502, detail="LLM 请求频率超限，请稍后重试") from exc
    except openai.APITimeoutError as exc:
        raise HTTPException(status_code=504, detail="LLM 响应超时，请稍后重试") from exc
    return {"code": 0, "data": SummaryOut.model_validate(summary).model_dump(), "msg": "ok"}


@router.get("/meetings/{meeting_id}/summaries", response_model=dict)
async def list_summaries(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)
    summaries = await summary_service.list_summaries(db, meeting_id)
    return {
        "code": 0,
        "data": [SummaryOut.model_validate(s).model_dump() for s in summaries],
        "msg": "ok",
    }


@router.put("/summaries/{summary_id}", response_model=dict)
async def update_summary(
    summary_id: uuid.UUID,
    data: SummaryUpdate,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    summary = await summary_service.get_summary(db, summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="纪要不存在")
    summary = await summary_service.update_summary(db, summary, data)
    return {"code": 0, "data": SummaryOut.model_validate(summary).model_dump(), "msg": "ok"}
