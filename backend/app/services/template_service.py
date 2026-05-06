import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.template import MeetingTemplate
from app.schemas.template import TemplateCreate, TemplateUpdate


async def list_templates(
    db: AsyncSession, owner_id: uuid.UUID | None = None
) -> list[MeetingTemplate]:
    stmt = select(MeetingTemplate)
    if owner_id is not None:
        # Regular user: system templates (owner_id IS NULL) + own templates
        stmt = stmt.where(
            or_(MeetingTemplate.owner_id.is_(None), MeetingTemplate.owner_id == owner_id)
        )
    stmt = stmt.order_by(MeetingTemplate.created_at)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_template(db: AsyncSession, template_id: uuid.UUID) -> MeetingTemplate | None:
    result = await db.execute(
        select(MeetingTemplate).where(MeetingTemplate.id == template_id)
    )
    return result.scalar_one_or_none()


async def create_template(
    db: AsyncSession, data: TemplateCreate, owner_id: uuid.UUID | None = None
) -> MeetingTemplate:
    template = MeetingTemplate(**data.model_dump(), owner_id=owner_id)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def update_template(
    db: AsyncSession, template: MeetingTemplate, data: TemplateUpdate
) -> MeetingTemplate:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    await db.commit()
    await db.refresh(template)
    return template


async def delete_template(db: AsyncSession, template: MeetingTemplate) -> None:
    await db.delete(template)
    await db.commit()
