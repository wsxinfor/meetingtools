import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateOut, TemplateUpdate
from app.services import template_service

router = APIRouter(tags=["templates"])


def _check_template_write(template, current_user: User) -> None:
    """Admin can edit anything; regular users can only edit their own templates."""
    if current_user.role == "admin":
        return
    if template.owner_id is None or template.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改该模板")


@router.get("/templates", response_model=dict)
async def list_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    owner_filter = None if current_user.role == "admin" else current_user.id
    templates = await template_service.list_templates(db, owner_id=owner_filter)
    return {
        "code": 0,
        "data": [TemplateOut.model_validate(t).model_dump() for t in templates],
        "msg": "ok",
    }


@router.post("/templates", response_model=dict)
async def create_template(
    data: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    # Admins create system templates (owner_id=None); regular users own their templates
    owner_id = None if current_user.role == "admin" else current_user.id
    template = await template_service.create_template(db, data, owner_id=owner_id)
    return {"code": 0, "data": TemplateOut.model_validate(template).model_dump(), "msg": "ok"}


@router.get("/templates/{template_id}", response_model=dict)
async def get_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    template = await template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {"code": 0, "data": TemplateOut.model_validate(template).model_dump(), "msg": "ok"}


@router.put("/templates/{template_id}", response_model=dict)
async def update_template(
    template_id: uuid.UUID,
    data: TemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    template = await template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    _check_template_write(template, current_user)
    template = await template_service.update_template(db, template, data)
    return {"code": 0, "data": TemplateOut.model_validate(template).model_dump(), "msg": "ok"}


@router.delete("/templates/{template_id}", response_model=dict)
async def delete_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    template = await template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    _check_template_write(template, current_user)
    await template_service.delete_template(db, template)
    return {"code": 0, "data": None, "msg": "ok"}
