import pytest
from config import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient, Response

tags_url: str = "/arts/tags"
search_url: str = "/arts/tags/search"


class TestTagsPost:
    async def test_without_token(self, async_client: "AsyncClient") -> None:
        body: dict = {"tag_name": "TagName"}
        response: "Response" = await async_client.post(tags_url, json=body)
        assert response.status_code == 401

    async def test_ordinary_user(self, async_client: "AsyncClient", token_1: str) -> None:
        headers: dict = {"Authorization": f"Bearer {token_1}"}
        body: dict = {"tag_name": "TagName"}
        response: "Response" = await async_client.post(tags_url, json=body, headers=headers)
        assert response.status_code == 403  # POST /arts/tags allowed for moderators

    @pytest.mark.parametrize(
        "tag_name",
        ["Anime", "Wallpaper", "Art"],
    )
    async def test_moderator(
            self, async_client: "AsyncClient", token_2: str, tag_name: str
    ) -> None:
        headers: dict = {"Authorization": f"Bearer {token_2}"}
        body: dict = {"tag_name": tag_name}
        response: "Response" = await async_client.post(tags_url, json=body, headers=headers)
        assert response.status_code == 201  # token_2 is moderator


@pytest.mark.parametrize(
    "tag_part, expected_tags",
    [
        ("a", ["Anime", "Art"]),
        ("A", ["Anime", "Art"]),
        ("w", ["Wallpaper"]),
        ("wAL", ["Wallpaper"]),
        ("s", [])
    ]
)
async def test_get_tags_search(
        async_client: "AsyncClient", tag_part: str, expected_tags: list[str]
) -> None:
    response: "Response" = await async_client.get(search_url, params={"tag_part": tag_part})
    result: list[dict] = response.json()

    assert response.status_code == 200
    assert [tag["name"] for tag in result] == expected_tags


class TestDeleteTags:
    # !! IMPORTANT !!: THESE TESTS DEPENDS ON TestPostTags
    async def test_without_token(self, async_client: "AsyncClient") -> None:
        response_1: "Response" = await async_client.request(
            method="DELETE", url=tags_url, json={"tag_id": 1}
        )
        assert response_1.status_code == 401

    async def test_ordinary_user(self, async_client: "AsyncClient", token_1: str) -> None:
        headers: dict = {"Authorization": f"Bearer {token_1}"}

        response: "Response" = await async_client.request(
            method="DELETE", url=tags_url, json={"tag_id": 1}, headers=headers
        )
        assert response.status_code == 403

    async def test_moderator(self, async_client: "AsyncClient", token_2: str) -> None:
        headers: dict = {"Authorization": f"Bearer {token_2}"}

        for i in range(3):
            response_3: "Response" = await async_client.request(
                method="DELETE", url=tags_url, json={"tag_id": i}, headers=headers
            )
            assert response_3.status_code == 200
