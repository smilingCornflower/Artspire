from typing import TYPE_CHECKING
import pytest
from src.database.db import db_manager
from sqlalchemy import text

if TYPE_CHECKING:
    from httpx import AsyncClient, Response


async def prepare_db() -> None:
    async with db_manager.async_session_maker() as session:
        async with session.begin():
            stmt: str = "INSERT INTO roles (name) values ('user'), ('moderator')"
            await session.execute(text(stmt))


@pytest.fixture(scope="module", autouse=True)
async def setup_db_test_save():
    await prepare_db()


class Endpoints:
    register = "/users/register"


endpoints = Endpoints()


async def test_register(async_client: "AsyncClient"):
    user_data = {
        "username": "nickname",
        "email": "user@example.com",
        "password": "12345678"
    }
    response: "Response" = await async_client.post(endpoints.register, data=user_data)

    assert response.status_code == 201
    assert response.json() == 1