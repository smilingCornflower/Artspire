import pytest
import asyncio
from typing import TYPE_CHECKING
from src.config import logger
from os import path

if TYPE_CHECKING:
    from httpx import Response
    from typing import Any

cur_dir = path.dirname(__file__)


async def test_post_arts(async_client, token):
    query_params: list[dict] = [
        {"art_title": "title_1", "art_tags": "tag1,tag2,tag3"},
        {"art_title": "title_2", "art_tags": "tag3,tag4,tag5"},
        {"art_title": "title_3", "art_tags": "tag5,tag6,tag7"},
    ]
    headers = {"Authorization": f"Bearer {token}"}
    images: list[dict] = [
        {"art_file": ("image_1.jpg", open(f"{cur_dir}/images/image_1.jpg", "rb"), "image/jpeg")},
        {"art_file": ("image_2.png", open(f"{cur_dir}/images/image_2.png", "rb"), "image/jpeg")},
        {"art_file": ("image_3.webp", open(f"{cur_dir}/images/image_3.webp", "rb"), "image/jpeg")},
    ]
    for i in range(3):
        response: "Response" = await async_client.post(
            "/arts", params=query_params[i], headers=headers, files=images[i]
        )
        assert response.status_code == 201


class TestArtsGet:
    async def test_without_params(self, async_client):
        # IMPORTANT: this test depends on test_post_arts()
        response: "Response" = await async_client.get("/arts")
        result: "Any" = response.json()

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
    async def test_with_offset_limit(self, async_client, offset, limit, length, status_code):
        logger.debug(f"offset: {offset}, limit: {limit}, length: {length}, status: {status_code}")
        query_params: dict[str, int] = {"offset": offset, "limit": limit}
        response: "Response" = await async_client.get("/arts", params=query_params)
        result: list[dict] = response.json()

        assert response.status_code == status_code
        if length:
            assert len(result) == length
