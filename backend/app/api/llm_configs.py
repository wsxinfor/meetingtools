import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.schemas.llm_config import LlmConfigCreate, LlmConfigOut, LlmConfigUpdate
from app.services import llm_config_service
from app.services.llm import provider as llm_provider

logger = logging.getLogger(__name__)
router = APIRouter(tags=["llm-configs"])


@router.get("/llm-configs", response_model=dict)
async def list_llm_configs(
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    configs = await llm_config_service.list_configs(db)
    return {
        "code": 0,
        "data": [LlmConfigOut.model_validate(c).model_dump() for c in configs],
        "msg": "ok",
    }


@router.post("/llm-configs", response_model=dict)
async def create_llm_config(
    data: LlmConfigCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    config = await llm_config_service.create_config(db, data)
    return {"code": 0, "data": LlmConfigOut.model_validate(config).model_dump(), "msg": "ok"}


@router.put("/llm-configs/{config_id}", response_model=dict)
async def update_llm_config(
    config_id: uuid.UUID,
    data: LlmConfigUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    config = await llm_config_service.get_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="LLM配置不存在")
    config = await llm_config_service.update_config(db, config, data)
    return {"code": 0, "data": LlmConfigOut.model_validate(config).model_dump(), "msg": "ok"}


@router.delete("/llm-configs/{config_id}", response_model=dict)
async def delete_llm_config(
    config_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    config = await llm_config_service.get_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="LLM配置不存在")
    await llm_config_service.delete_config(db, config)
    return {"code": 0, "data": None, "msg": "ok"}


@router.put("/llm-configs/{config_id}/set-default", response_model=dict)
async def set_default_config(
    config_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    config = await llm_config_service.get_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="LLM配置不存在")
    config = await llm_config_service.set_default(db, config)
    return {"code": 0, "data": LlmConfigOut.model_validate(config).model_dump(), "msg": "ok"}


@router.post("/llm-configs/{config_id}/test", response_model=dict)
async def test_llm_config(
    config_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    config = await llm_config_service.get_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="LLM配置不存在")
    try:
        import asyncio
        result = await asyncio.get_event_loop().run_in_executor(
            None, llm_provider.test_connection, config
        )
        return {
            "code": 0,
            "data": {
                "success": True,
                "latency_ms": result.latency_ms,
                "sample_output": result.content[:200],
            },
            "msg": "ok",
        }
    except Exception as exc:
        logger.warning("LLM test failed config_id=%s: %s", config_id, exc)
        return {
            "code": 1,
            "data": {"success": False, "error": str(exc)},
            "msg": str(exc),
        }
