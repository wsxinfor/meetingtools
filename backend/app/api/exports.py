import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.export_record import ExportRecordOut, ExportRequest
from app.services import export_service, meeting_service, summary_service

router = APIRouter(tags=["exports"])

_ALLOWED_FORMATS = {"md", "docx"}


def _check_meeting_access(meeting, current_user: User) -> None:
    if current_user.role != "admin" and meeting.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="会议不存在")


@router.post("/meetings/{meeting_id}/export-transcript", response_model=dict)
async def export_transcript(
    meeting_id: uuid.UUID,
    data: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if data.format not in _ALLOWED_FORMATS:
        raise HTTPException(status_code=400, detail=f"不支持的格式：{data.format}")
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    _check_meeting_access(meeting, current_user)
    record = await export_service.export_transcript(db, meeting, data.format)
    return {"code": 0, "data": ExportRecordOut.model_validate(record).model_dump(), "msg": "ok"}


@router.post("/summaries/{summary_id}/export", response_model=dict)
async def export_summary(
    summary_id: uuid.UUID,
    data: ExportRequest,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if data.format not in _ALLOWED_FORMATS:
        raise HTTPException(status_code=400, detail=f"不支持的格式：{data.format}")
    summary = await summary_service.get_summary(db, summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="纪要不存在")
    record = await export_service.export_summary(db, summary, data.format)
    return {"code": 0, "data": ExportRecordOut.model_validate(record).model_dump(), "msg": "ok"}


@router.get("/export-records/{export_id}/download")
async def download_export(
    export_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    record = await export_service.get_export_record(db, export_id)
    if not record:
        raise HTTPException(status_code=404, detail="导出记录不存在")
    path = Path(record.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="导出文件不存在")
    media_type = "text/markdown" if record.file_format == "md" else (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    return FileResponse(path=str(path), media_type=media_type, filename=path.name)
