from typing import TYPE_CHECKING
import pytest
import asyncio
from src.database.db import db_manager
from src.config import logger

from sqlalchemy import text
from sqlalchemy import insert

from datetime import datetime

if TYPE_CHECKING:
    from httpx import AsyncClient, Response
    from sqlalchemy import Insert, TextClause

save_url: str = "/arts/save"


async def prepare_db() -> None:
    async with db_manager.async_session_maker() as session:
        async with session.begin():
            # noinspection SqlInsertValues
            stmt: str = (
                f"INSERT INTO arts"
                f" (user_id, blob_name, url, url_generated_at) VALUES"
                f" (1, 'blob_1', 'url_1', clock_timestamp()),"
                f" (1, 'blob_2', 'url_2', clock_timestamp()),"
                f" (1, 'blob_3', 'url_3', clock_timestamp()),"
                f" (1, 'blob_4', 'url_4', clock_timestamp()),"
                f" (1, 'blob_5', 'url_5', clock_timestamp());"
            )
            await session.execute(text(stmt))


@pytest.fixture(scope="module", autouse=True)
async def setup_db_test_save():
    await prepare_db()


class TestPostSave:
    async def test_without_token(
            self, async_client: "AsyncClient"
    ) -> None:
        response: "Response" = await async_client.post(save_url, json={"art_id": 1})
        assert response.status_code == 401

    @pytest.mark.parametrize("art_id", [1, 2, 3, 4])
    async def test_with_token_1(
            self, async_client: "AsyncClient", token_1: str, art_id: int,
    ) -> None:
        headers: dict = {"Authorization": f"Bearer {token_1}"}
        response: "Response" = await async_client.post(
            save_url, json={"art_id": art_id}, headers=headers
        )
        assert response.status_code == 201


class TestGetSave:
    async def test_without_token(
            self, async_client: "AsyncClient",
    ) -> None:
        response: "Response" = await async_client.get(save_url)
        assert response.status_code == 401

    async def test_with_token(
            self, async_client: "AsyncClient", token_1: str
    ) -> None:
        headers: dict = {"Authorization": f"Bearer {token_1}"}
        response: "Response" = await async_client.get(save_url, headers=headers)
        result: list[dict] = response.json()

        assert response.status_code == 200
        assert len(result) == 4

    @pytest.mark.parametrize(
        "offset, limit, length, status_code",
        [(0, 10, 4, 200), (0, 2, 2, 200), (10, 10, None, 404)]
    )
    async def test_offset_limit(
            self,
            async_client: "AsyncClient",
            token_1: str,
            offset: int,
            limit: int,
            length: int,
            status_code: int,
    ) -> None:
        headers: dict = {"Authorization": f"Bearer {token_1}"}
        query_params: dict = {"offset": offset, "limit": limit}
        response: "Response" = await async_client.get(save_url, params=query_params,
                                                      headers=headers)

        assert response.status_code == status_code
        if length:
            assert len(response.json()) == length


class TestDeleteSave:
    async def test_without_token(self, async_client: "AsyncClient") -> None:
        response: "Response" = await async_client.request(
            method="DELETE", url=save_url, json={"art_id": 1},
        )
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "art_id, status_code, result",
        [(1, 200, True), (2, 200, True), (3, 200, True), (4, 200, True), (5, 200, False)]
    )
    async def test_with_token(
            self,
            async_client: "AsyncClient",
            token_1: str,
            art_id: int,
            status_code: int,
            result: bool
    ) -> None:
        headers: dict = {"Authorization": f"Bearer {token_1}"}
        response: "Response" = await async_client.request(
            method="DELETE", url=save_url, json={"art_id": art_id}, headers=headers,
        )
        assert response.status_code == status_code
        assert response.json() is result
