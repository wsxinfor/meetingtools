import logging
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.asr_config import AsrConfigCreate, AsrConfigOut, AsrConfigUpdate
from app.services import asr_config_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["asr-configs"])


@router.get("/asr-configs", response_model=dict)
async def list_asr_configs(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    configs = await asr_config_service.list_configs(db)
    return {
        "code": 0,
        "data": [AsrConfigOut.model_validate(c).model_dump() for c in configs],
        "msg": "ok",
    }


@router.post("/asr-configs", response_model=dict)
async def create_asr_config(
    data: AsrConfigCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    config = await asr_config_service.create_config(db, data)
    return {"code": 0, "data": AsrConfigOut.model_validate(config).model_dump(), "msg": "ok"}


@router.put("/asr-configs/{config_id}", response_model=dict)
async def update_asr_config(
    config_id: uuid.UUID,
    data: AsrConfigUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    config = await asr_config_service.get_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="ASR配置不存在")
    config = await asr_config_service.update_config(db, config, data)
    return {"code": 0, "data": AsrConfigOut.model_validate(config).model_dump(), "msg": "ok"}


@router.delete("/asr-configs/{config_id}", response_model=dict)
async def delete_asr_config(
    config_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    config = await asr_config_service.get_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="ASR配置不存在")
    await asr_config_service.delete_config(db, config)
    return {"code": 0, "data": None, "msg": "ok"}


@router.put("/asr-configs/{config_id}/set-default", response_model=dict)
async def set_default_asr_config(
    config_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    config = await asr_config_service.get_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="ASR配置不存在")
    config = await asr_config_service.set_default(db, config)
    return {"code": 0, "data": AsrConfigOut.model_validate(config).model_dump(), "msg": "ok"}


@router.post("/asr-configs/{config_id}/test", response_model=dict)
async def test_asr_config(
    config_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    config = await asr_config_service.get_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="ASR配置不存在")
    if config.provider == "local":
        return {"code": 0, "data": {"success": True, "message": "本地服务无需测试"}, "msg": "ok"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{config.base_url.rstrip('/')}/v1/transcriptions",
                headers={"Authorization": f"Bearer {config.api_key}"},
            )
            if resp.status_code in (200, 401):
                if resp.status_code == 401:
                    return {
                        "code": 1,
                        "data": {"success": False, "error": "API Key 无效或未授权"},
                        "msg": "认证失败",
                    }
                return {"code": 0, "data": {"success": True}, "msg": "ok"}
            return {
                "code": 1,
                "data": {"success": False, "error": f"HTTP {resp.status_code}"},
                "msg": f"连接异常: HTTP {resp.status_code}",
            }
    except httpx.ConnectError:
        return {
            "code": 1,
            "data": {"success": False, "error": "无法连接到远程服务"},
            "msg": "连接失败",
        }
    except httpx.TimeoutException:
        return {
            "code": 1,
            "data": {"success": False, "error": "连接超时"},
            "msg": "连接超时",
        }
    except Exception as exc:
        logger.warning("ASR config test failed config_id=%s: %s", config_id, exc)
        return {"code": 1, "data": {"success": False, "error": str(exc)}, "msg": str(exc)}
