from typing import TYPE_CHECKING
import pytest
import asyncio
from httpx import AsyncClient

from models import Base

from src.main import app

from src.database.db import db_manager

from src.config import settings
from src.config import logger

if TYPE_CHECKING:
    from asyncio.events import AbstractEventLoop
    from httpx import Response
    from sqlalchemy.ext.asyncio import AsyncEngine
    from typing import AsyncGenerator

AUTH_SERVER: str = f"http://{settings.server.host}:{settings.server.auth_port}"
ARTS_SERVER: str = f"http://{settings.server.host}:{settings.server.arts_port}"


# SETUP
@pytest.fixture(scope="session")
def event_loop(request):
    loop: "AbstractEventLoop" = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    assert settings.mode == "TEST"
    logger.warning(f"MODE={settings.mode}")
    async with db_manager.engine.begin() as connection:
        connection: "AsyncEngine"
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with db_manager.engine.begin() as connection:
        connection: "AsyncEngine"
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session", autouse=True)
async def async_client() -> "AsyncGenerator[AsyncClient, None]":
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def token() -> str:
    data = {"username": "test_user", "password": "test_user"}
    async with AsyncClient(base_url=AUTH_SERVER) as ac:
        response: "Response" = await ac.post("/users/login", data=data)

    assert response.status_code == 200

    access_token: str = response.json()["access_token"]
    logger.debug(f"access_token: {access_token[:50]}")
    return access_token
