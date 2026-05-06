import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.asr_task import AsrTaskCreate, AsrTaskOut
from app.services import asr_task_service, audio_service, meeting_service

router = APIRouter(tags=["asr"])


def _check_meeting_access(meeting, current_user: User) -> None:
    if current_user.role != "admin" and meeting.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="会议不存在")


@router.post("/meetings/{meeting_id}/asr-tasks", response_model=dict)
async def start_asr_task(
    meeting_id: uuid.UUID,
    body: AsrTaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)

    audio_file = await audio_service.get_audio_file(db, body.audio_file_id)
    if not audio_file or audio_file.meeting_id != meeting_id:
        raise HTTPException(status_code=404, detail="音频文件不存在")
    if audio_file.status != "preprocessed":
        raise HTTPException(status_code=422, detail="音频文件尚未完成预处理，请稍候再试")

    task = await asr_task_service.create_asr_task(
        db, meeting_id, body.audio_file_id, body.engine
    )
    return {"code": 0, "data": AsrTaskOut.model_validate(task).model_dump(), "msg": "ok"}


@router.get("/asr-tasks/{task_id}", response_model=dict)
async def get_asr_task(
    task_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    task = await asr_task_service.get_asr_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"code": 0, "data": AsrTaskOut.model_validate(task).model_dump(), "msg": "ok"}
