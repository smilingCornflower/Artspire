import pytest
import asyncio

import requests
from httpx import request
from typing import TYPE_CHECKING
from src.config import logger
from os import path
from src.services.arts import ArtsService

if TYPE_CHECKING:
    from httpx import Response, AsyncClient
    from typing import Any

cur_dir = path.dirname(__file__)
arts_url: str = "/arts"


class TestArtsPost:
    query_params: list[dict] = [
        {"art_title": "title_1", "art_tags": "tag1,tag2,tag3"},
        {"art_title": "title_2", "art_tags": "tag3,tag4,tag5"},
        {"art_title": "title_3", "art_tags": "tag5,tag6,tag7"},
    ]
    images: list[dict] = [
        {"art_file": ("image_1.jpg", open(f"{cur_dir}/images/image_1.jpg", "rb"), "image/jpeg")},
        {"art_file": ("image_2.png", open(f"{cur_dir}/images/image_2.png", "rb"), "image/jpeg")},
        {"art_file": ("image_3.webp", open(f"{cur_dir}/images/image_3.webp", "rb"), "image/jpeg")},
    ]

    async def test_without_token(self, async_client: "AsyncClient") -> None:
        response: "Response" = await async_client.post(
            arts_url, params=self.query_params[0], files=self.images[0]
        )
        assert response.status_code == 401

    async def test_with_token(
            self, async_client: "AsyncClient", token_1: str, token_2: str
    ) -> None:
        headers: list[dict] = [{"Authorization": f"Bearer {token_1}"},
                               {"Authorization": f"Bearer {token_1}"},
                               {"Authorization": f"Bearer {token_2}"}]
        for i in range(3):
            response: "Response" = await async_client.post(
                arts_url, params=self.query_params[i], headers=headers[i], files=self.images[i]
            )
            assert response.status_code == 201


class TestArtsGet:
    async def test_without_params(self, async_client: "AsyncClient") -> None:
        # !! IMPORTANT !!: THIS TEST DEPENDS ON TestArtsPost
        response: "Response" = await async_client.get(arts_url)
        result: "Any" = response.json()
        logger.debug(f"result GET: {result}")

        assert response.status_code == 200
        assert len(result) == 3

    @pytest.mark.parametrize(
        "offset, limit, length, status_code",
        [
            (0, 10, 3, 200),
            (1, 10, 2, 200),
            (10, 10, None, 404),
        ]
    )
    async def test_with_offset_limit(
            self,
            async_client: int,
            offset: int,
            limit: int,
            length: int,
            status_code: int
    ) -> None:
        logger.debug(f"offset: {offset}, limit: {limit}, length: {length}, status: {status_code}")
        query_params: dict[str, int] = {"offset": offset, "limit": limit}
        response: "Response" = await async_client.get("/arts", params=query_params)
        result: list[dict] = response.json()

        assert response.status_code == status_code
        if length:
            assert len(result) == length

    async def test_with_tags(self, async_client: "AsyncClient") -> None:
        query_params: dict = {"art_id": 1, "include_tags": True, "status_code": 200}
        response: "Response" = await async_client.get("/arts", params=query_params)
        result: list[dict] = response.json()
        art: dict = result[0]

        assert response.status_code == 200
        assert len(art["tags"]) == 3


# TODO: Test, moderator deletes an art of another user
class TestArtsDelete:
    async def test_without_token(
            self,
            async_client: "AsyncClient"
    ) -> None:
        response: "Response" = await async_client.request(
            method="DELETE", url=arts_url, json={"art_id": 1}
        )
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "art_id, status_code",
        [(1, 200), (2, 200), (3, 403), (4, 404)]
    )
    # art_id=3 was published by test_user_2, so 403(Forbidden) for DELETE(/arts) from test_user_1
    # art_id=4 does not exist
    async def test_with_token(
            self,
            async_client: "AsyncClient",
            art_id: int,
            status_code: int,
            token_1: str
    ) -> None:
        headers = {"Authorization": f"Bearer {token_1}"}
        body: dict = {"art_id": art_id}
        response: "Response" = await async_client.request(
            method="DELETE", url=arts_url, json=body, headers=headers
        )

        assert response.status_code == status_code

    async def test_third_art(self, async_client, token_2) -> None:
        headers = {"Authorization": f"Bearer {token_2}"}
        body: dict = {"art_id": 3}
        response: "Response" = await async_client.request(
            method="DELETE", url=arts_url, json=body, headers=headers
        )

        assert response.status_code == 200
