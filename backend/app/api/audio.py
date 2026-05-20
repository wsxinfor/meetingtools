import os
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.audio import AudioFileOut
from app.services import audio_service, meeting_service

router = APIRouter(tags=["audio"])

_ALLOWED = {".mp3", ".wav", ".m4a", ".aac", ".webm"}
_CHUNK = 1024 * 1024  # 1 MB


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

    # 流式写入临时文件，边写边检查大小，避免大文件全量读入内存
    fd, tmp_path_str = tempfile.mkstemp(suffix=suffix)
    tmp_path = Path(tmp_path_str)
    total = 0
    try:
        with os.fdopen(fd, "wb") as tmp_f:
            while chunk := await file.read(_CHUNK):
                total += len(chunk)
                if total > audio_service.MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"文件超过 {audio_service.MAX_FILE_SIZE // (1024 ** 3)} GB 限制",
                    )
                tmp_f.write(chunk)

        audio_file = await audio_service.save_audio_file(
            db, meeting_id, file.filename or "audio", tmp_path
        )
    except HTTPException:
        tmp_path.unlink(missing_ok=True)
        raise
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

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


@router.delete("/audio-files/{audio_file_id}", response_model=dict)
async def delete_audio_file(
    audio_file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    audio_file = await audio_service.get_audio_file(db, audio_file_id)
    if not audio_file:
        raise HTTPException(status_code=404, detail="音频文件不存在")
    meeting = await meeting_service.get_meeting(db, audio_file.meeting_id)
    if meeting:
        _check_meeting_access(meeting, current_user)
    await audio_service.delete_audio_file(db, audio_file)
    return {"code": 0, "data": None, "msg": "ok"}


_MEDIA_TYPES = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".webm": "audio/webm",
    ".ogg": "audio/ogg",
}


@router.get("/audio-files/{audio_file_id}/download")
async def download_audio_file(
    audio_file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    audio_file = await audio_service.get_audio_file(db, audio_file_id)
    if not audio_file:
        raise HTTPException(status_code=404, detail="音频文件不存在")
    meeting = await meeting_service.get_meeting(db, audio_file.meeting_id)
    if meeting:
        _check_meeting_access(meeting, current_user)
    path = Path(audio_file.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="音频文件不存在")
    media_type = _MEDIA_TYPES.get(path.suffix.lower(), "application/octet-stream")
    return FileResponse(
        path=str(path),
        media_type=media_type,
        filename=audio_file.original_filename,
    )
