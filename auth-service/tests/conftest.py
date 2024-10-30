from typing import TYPE_CHECKING
import pytest
import asyncio
from httpx import AsyncClient
from dotenv import load_dotenv
from models import Base
import os
from src.main import app
from src.database.db import db_manager
from src.config import settings, logger

if TYPE_CHECKING:
    from asyncio.events import AbstractEventLoop
    from httpx import Response
    from sqlalchemy.ext.asyncio import AsyncEngine
    from typing import AsyncGenerator


# SETUP
@pytest.fixture(scope="session")
def event_loop(request):
    loop: "AbstractEventLoop" = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    assert settings.mode == "TEST"
    assert settings.db_name == "test_db_auth"

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
