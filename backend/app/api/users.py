import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=dict)
async def list_users(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    users = await user_service.list_users(db)
    return {"code": 0, "data": [UserOut.model_validate(u).model_dump() for u in users], "msg": "ok"}


@router.post("", response_model=dict)
async def create_user(
    data: UserCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    existing = await user_service.get_user_by_username(db, data.username)
    if existing:
        raise HTTPException(status_code=409, detail="用户名已存在")
    user = await user_service.create_user(db, data)
    return {"code": 0, "data": UserOut.model_validate(user).model_dump(), "msg": "ok"}


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # Prevent admin from removing their own admin role or deactivating themselves
    if user.id == current_user.id:
        if data.role == "user":
            raise HTTPException(status_code=400, detail="不能修改自己的角色")
        if data.is_active is False:
            raise HTTPException(status_code=400, detail="不能禁用自己的账号")
    user = await user_service.update_user(db, user, data)
    return {"code": 0, "data": UserOut.model_validate(user).model_dump(), "msg": "ok"}


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")
    await user_service.delete_user(db, user)
    return {"code": 0, "data": None, "msg": "ok"}


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)) -> dict:
    return {"code": 0, "data": UserOut.model_validate(current_user).model_dump(), "msg": "ok"}
