import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.meeting import Meeting, Project
from app.schemas.meeting import ProjectCreate, ProjectOut, ProjectUpdate
from app.services import meeting_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=dict)
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)) -> dict:
    project = await meeting_service.create_project(db, data)
    return {"code": 0, "data": ProjectOut.model_validate(project).model_dump(), "msg": "ok"}


@router.get("", response_model=dict)
async def list_projects(
    customer_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    projects = await meeting_service.list_projects(db, customer_id)
    return {
        "code": 0,
        "data": [ProjectOut.model_validate(p).model_dump() for p in projects],
        "msg": "ok",
    }


@router.get("/{project_id}", response_model=dict)
async def get_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    project = await meeting_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return {"code": 0, "data": ProjectOut.model_validate(project).model_dump(), "msg": "ok"}


@router.put("/{project_id}", response_model=dict)
async def update_project(
    project_id: uuid.UUID, data: ProjectUpdate, db: AsyncSession = Depends(get_db)
) -> dict:
    project = await meeting_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    project = await meeting_service.update_project(db, project, data)
    return {"code": 0, "data": ProjectOut.model_validate(project).model_dump(), "msg": "ok"}


@router.delete("/{project_id}", response_model=dict)
async def delete_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    project = await meeting_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    count = (
        await db.execute(select(func.count()).select_from(Meeting).where(Meeting.project_id == project_id))
    ).scalar_one()
    if count > 0:
        raise HTTPException(status_code=400, detail="该项目下存在会议，无法删除")
    await meeting_service.delete_project(db, project)
    return {"code": 0, "data": None, "msg": "ok"}
