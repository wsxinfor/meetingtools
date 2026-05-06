import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.llm_config import LlmConfig
from app.schemas.llm_config import LlmConfigCreate, LlmConfigUpdate


async def list_configs(db: AsyncSession) -> list[LlmConfig]:
    result = await db.execute(select(LlmConfig).order_by(LlmConfig.created_at))
    return list(result.scalars().all())


async def get_config(db: AsyncSession, config_id: uuid.UUID) -> LlmConfig | None:
    result = await db.execute(select(LlmConfig).where(LlmConfig.id == config_id))
    return result.scalar_one_or_none()


async def get_default_config(db: AsyncSession) -> LlmConfig | None:
    result = await db.execute(
        select(LlmConfig).where(LlmConfig.is_default.is_(True), LlmConfig.is_enabled.is_(True))
    )
    return result.scalar_one_or_none()


async def create_config(db: AsyncSession, data: LlmConfigCreate) -> LlmConfig:
    if data.is_default:
        await _clear_default(db)
    config = LlmConfig(**data.model_dump())
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


async def update_config(db: AsyncSession, config: LlmConfig, data: LlmConfigUpdate) -> LlmConfig:
    if data.is_default is True:
        await _clear_default(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    await db.commit()
    await db.refresh(config)
    return config


async def set_default(db: AsyncSession, config: LlmConfig) -> LlmConfig:
    await _clear_default(db)
    config.is_default = True
    await db.commit()
    await db.refresh(config)
    return config


async def delete_config(db: AsyncSession, config: LlmConfig) -> None:
    await db.delete(config)
    await db.commit()


async def _clear_default(db: AsyncSession) -> None:
    await db.execute(update(LlmConfig).values(is_default=False))
    await db.flush()
