import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.meeting import ProjectCreate, ProjectOut
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
