from typing import TYPE_CHECKING
import pytest

from src.database.db import db_manager
from src.config import logger
from sqlalchemy import text

if TYPE_CHECKING:
    from httpx import AsyncClient, Response

like_url: str = "/arts/like"
arts_url: str = "/arts"


async def prepare_db() -> None:
    async with db_manager.async_session_maker() as session:
        async with session.begin():
            # noinspection SqlInsertValues
            stmt: str = (
                f"INSERT INTO arts"
                f" (user_id, blob_name, url, url_generated_at) VALUES"
                f" (1, 'blob_1', 'url_1', clock_timestamp()),"
                f" (1, 'blob_2', 'url_2', clock_timestamp());"
            )
            # !! IMPORTANT !!: USER WITH USER_ID MUST EXISTS IN THE DATABASE
            await session.execute(text(stmt))


@pytest.fixture(scope="module", autouse=True)
async def setup_db_test_save():
    await prepare_db()


class TestLikePost:
    body: dict = {"art_id": 1}

    async def test_without_token(self, async_client: "AsyncClient") -> None:
        response: "Response" = await async_client.post(like_url, params=self.body)
        assert response.status_code == 401

    async def test_with_tokens(
            self, async_client: "AsyncClient", token_1: dict, token_2: dict
    ) -> None:
        for token in [token_1, token_2]:
            response: "Response" = await async_client.post(
                like_url, json=self.body, headers=token
            )
            assert response.status_code == 201

        response: "Response" = await async_client.get(arts_url, params=self.body)
        result: dict = response.json()[0]
        assert result["likes_count"] == 2


class TestLikeGet:
    async def test_likes_in_arts_get(self, async_client: "AsyncClient", token_1: dict) -> None:
        response_1: "Response" = await async_client.get(
            "/arts", params={"art_id": 1}, headers=token_1
        )
        response_2: "Response" = await async_client.get(
            "/arts", params={"art_id": 2}, headers=token_1
        )

        logger.debug(f"result_1: {response_1.json()}")
        logger.debug(f"result_2: {response_1.json()}")

        assert response_1.json()[0]["is_liked"] is True
        assert response_2.json()[0]["is_liked"] is False


class TestLikeDelete:
    body: dict = {"art_id": 1}

    async def test_without_token(self, async_client: "AsyncClient") -> None:
        response: "Response" = await async_client.request(
            method="DELETE", url=like_url, params=self.body,
        )
        assert response.status_code == 401

    async def test_with_tokens(
            self, async_client: "AsyncClient", token_1: str, token_2: dict
    ) -> None:
        parameters = [
            (token_1, True, 1),
            (token_2, True, 0),
            (token_1, False, 0)
        ]
        for token, expected_del_result, expected_likes in parameters:
            delete_response: "Response" = await async_client.request(
                method="DELETE", url=like_url, json=self.body, headers=token
            )
            delete_result: bool = delete_response.json()

            response_get: "Response" = await async_client.get(arts_url, params=self.body)
            result_art: dict = response_get.json()[0]
            result_likes: int = result_art["likes_count"]

            assert delete_response.status_code == 200
            assert delete_result == expected_del_result
            assert result_likes == expected_likes
