import asyncio
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import Meeting
from app.models.summary import MeetingSummary
from app.models.template import MeetingTemplate
from app.schemas.summary import SummaryCreate, SummaryUpdate
from app.services.llm import provider as llm_provider
from app.services.llm_config_service import get_config, get_default_config

logger = logging.getLogger(__name__)


async def list_summaries(db: AsyncSession, meeting_id: uuid.UUID) -> list[MeetingSummary]:
    result = await db.execute(
        select(MeetingSummary)
        .where(MeetingSummary.meeting_id == meeting_id)
        .order_by(MeetingSummary.created_at.desc())
    )
    return list(result.scalars().all())


async def get_summary(db: AsyncSession, summary_id: uuid.UUID) -> MeetingSummary | None:
    result = await db.execute(
        select(MeetingSummary).where(MeetingSummary.id == summary_id)
    )
    return result.scalar_one_or_none()


async def generate_summary(
    db: AsyncSession, meeting: Meeting, data: SummaryCreate
) -> MeetingSummary:
    template_result = await db.execute(
        select(MeetingTemplate).where(MeetingTemplate.id == data.template_id)
    )
    template = template_result.scalar_one_or_none()
    if not template:
        raise ValueError("模板不存在")

    if data.llm_config_id:
        llm_config = await get_config(db, data.llm_config_id)
    else:
        llm_config = await get_default_config(db)

    if not llm_config:
        raise ValueError("未找到可用的 LLM 配置，请先在设置中配置并启用一个 LLM")

    transcript = (
        meeting.corrected_text
        if data.source == "corrected_text"
        else meeting.raw_text
    ) or ""

    prompt = template.prompt_text.replace("{{transcript_text}}", transcript)

    result = await asyncio.get_event_loop().run_in_executor(
        None, llm_provider.generate, llm_config, prompt
    )

    summary = MeetingSummary(
        meeting_id=meeting.id,
        template_id=template.id,
        llm_config_id=llm_config.id,
        llm_model=result.model,
        title=f"{meeting.title} - {template.name}",
        content_md=result.content,
        version=1,
        is_final=False,
    )
    db.add(summary)
    await db.commit()
    await db.refresh(summary)
    logger.info("Summary generated meeting_id=%s model=%s", meeting.id, result.model)
    return summary


async def update_summary(
    db: AsyncSession, summary: MeetingSummary, data: SummaryUpdate
) -> MeetingSummary:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(summary, field, value)
    await db.commit()
    await db.refresh(summary)
    return summary
