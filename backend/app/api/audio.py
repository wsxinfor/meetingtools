import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.audio import AudioFileOut
from app.services import audio_service, meeting_service

router = APIRouter(tags=["audio"])

_ALLOWED = {".mp3", ".wav", ".m4a", ".aac", ".webm"}


def _check_meeting_access(meeting, current_user: User) -> None:
    if current_user.role != "admin" and meeting.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="会议不存在")


@router.post("/meetings/{meeting_id}/audio", response_model=dict)
async def upload_audio(
    meeting_id: uuid.UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _ALLOWED:
        raise HTTPException(status_code=400, detail=f"不支持的格式，仅限 {', '.join(_ALLOWED)}")

    content = await file.read()
    if len(content) > audio_service.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="文件超过 500 MB 限制")

    audio_file = await audio_service.save_audio_file(
        db, meeting_id, file.filename or "audio", content
    )
    return {"code": 0, "data": AudioFileOut.model_validate(audio_file).model_dump(), "msg": "ok"}


@router.get("/audio-files/{audio_file_id}", response_model=dict)
async def get_audio_file(
    audio_file_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    audio_file = await audio_service.get_audio_file(db, audio_file_id)
    if not audio_file:
        raise HTTPException(status_code=404, detail="音频文件不存在")
    return {"code": 0, "data": AudioFileOut.model_validate(audio_file).model_dump(), "msg": "ok"}


@router.get("/meetings/{meeting_id}/audio-files", response_model=dict)
async def list_audio_files(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)
    files = await audio_service.list_audio_files_for_meeting(db, meeting_id)
    return {
        "code": 0,
        "data": [AudioFileOut.model_validate(f).model_dump() for f in files],
        "msg": "ok",
    }
