import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import Customer, Meeting, Project
from app.schemas.meeting import (
    CustomerCreate,
    MeetingCreate,
    MeetingUpdate,
    ProjectCreate,
)


# --- Customer ---

async def create_customer(db: AsyncSession, data: CustomerCreate) -> Customer:
    customer = Customer(**data.model_dump())
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


async def list_customers(db: AsyncSession) -> list[Customer]:
    result = await db.execute(select(Customer).order_by(Customer.created_at.desc()))
    return list(result.scalars().all())


# --- Project ---

async def create_project(db: AsyncSession, data: ProjectCreate) -> Project:
    project = Project(**data.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def list_projects(db: AsyncSession, customer_id: uuid.UUID | None = None) -> list[Project]:
    stmt = select(Project).order_by(Project.created_at.desc())
    if customer_id is not None:
        stmt = stmt.where(Project.customer_id == customer_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


# --- Meeting ---

async def create_meeting(
    db: AsyncSession, data: MeetingCreate, owner_id: uuid.UUID | None = None
) -> Meeting:
    meeting = Meeting(**data.model_dump(), owner_id=owner_id)
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return meeting


async def list_meetings(
    db: AsyncSession,
    keyword: str | None,
    customer_id: uuid.UUID | None,
    project_id: uuid.UUID | None,
    status: str | None,
    page: int,
    page_size: int,
    owner_id: uuid.UUID | None = None,
) -> tuple[int, list[Meeting]]:
    stmt = select(Meeting)
    if owner_id is not None:
        stmt = stmt.where(Meeting.owner_id == owner_id)
    if keyword:
        stmt = stmt.where(Meeting.title.ilike(f"%{keyword}%"))
    if customer_id:
        stmt = stmt.where(Meeting.customer_id == customer_id)
    if project_id:
        stmt = stmt.where(Meeting.project_id == project_id)
    if status:
        stmt = stmt.where(Meeting.status == status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(Meeting.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(stmt)).scalars().all())
    return total, items


async def get_meeting(db: AsyncSession, meeting_id: uuid.UUID) -> Meeting | None:
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    return result.scalar_one_or_none()


async def update_meeting(
    db: AsyncSession, meeting: Meeting, data: MeetingUpdate
) -> Meeting:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(meeting, field, value)
    await db.commit()
    await db.refresh(meeting)
    return meeting


async def delete_meeting(db: AsyncSession, meeting: Meeting) -> None:
    await db.delete(meeting)
    await db.commit()


async def save_corrected_text(
    db: AsyncSession, meeting: Meeting, corrected_text: str
) -> Meeting:
    meeting.corrected_text = corrected_text
    await db.commit()
    await db.refresh(meeting)
    return meeting


async def update_speaker_map(
    db: AsyncSession, meeting: Meeting, speaker_map: dict[str, str]
) -> Meeting:
    meeting.speaker_map = speaker_map
    await db.commit()
    await db.refresh(meeting)
    return meeting
