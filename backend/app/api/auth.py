from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.schemas.user import LoginRequest, TokenResponse, UserOut
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=dict)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> dict:
    user = await user_service.get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    token = create_access_token(user.id, user.role)
    return {
        "code": 0,
        "data": TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserOut.model_validate(user),
        ).model_dump(),
        "msg": "ok",
    }
