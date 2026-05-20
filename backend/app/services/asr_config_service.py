import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asr_config import AsrConfig
from app.schemas.asr_config import AsrConfigCreate, AsrConfigUpdate


async def list_configs(db: AsyncSession) -> list[AsrConfig]:
    result = await db.execute(select(AsrConfig).order_by(AsrConfig.created_at))
    return list(result.scalars().all())


async def get_config(db: AsyncSession, config_id: uuid.UUID) -> AsrConfig | None:
    result = await db.execute(select(AsrConfig).where(AsrConfig.id == config_id))
    return result.scalar_one_or_none()


async def get_default_config(db: AsyncSession) -> AsrConfig | None:
    result = await db.execute(
        select(AsrConfig).where(AsrConfig.is_default.is_(True), AsrConfig.is_enabled.is_(True))
    )
    return result.scalar_one_or_none()


async def create_config(db: AsyncSession, data: AsrConfigCreate) -> AsrConfig:
    if data.is_default:
        await _clear_default(db)
    config = AsrConfig(**data.model_dump())
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


async def update_config(db: AsyncSession, config: AsrConfig, data: AsrConfigUpdate) -> AsrConfig:
    if data.is_default is True:
        await _clear_default(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    await db.commit()
    await db.refresh(config)
    return config


async def set_default(db: AsyncSession, config: AsrConfig) -> AsrConfig:
    await _clear_default(db)
    config.is_default = True
    await db.commit()
    await db.refresh(config)
    return config


async def delete_config(db: AsyncSession, config: AsrConfig) -> None:
    await db.delete(config)
    await db.commit()


async def _clear_default(db: AsyncSession) -> None:
    await db.execute(update(AsrConfig).values(is_default=False))
    await db.flush()
