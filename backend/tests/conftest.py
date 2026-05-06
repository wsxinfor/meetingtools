from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import get_db
from main import app

# NullPool avoids asyncpg connection pool binding to a specific event loop,
# which causes "Future attached to a different loop" errors in tests.
_test_engine = create_async_engine(settings.database_url, poolclass=NullPool)
_test_session_factory = async_sessionmaker(_test_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def _override_db() -> None:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with _test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    session = _test_session_factory()
    try:
        yield session
    finally:
        try:
            await session.close()
        except Exception:
            pass
