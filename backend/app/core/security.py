import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

_ALGORITHM = "HS256"
_EXPIRE_DAYS = 30


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)


def decode_token(token: str) -> dict:
    """Raises JWTError if token is invalid or expired."""
    return jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
