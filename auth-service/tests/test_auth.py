from typing import TYPE_CHECKING
import pytest
from src.database.db import db_manager
from sqlalchemy import text
from src.exceptions.http import HTTPExceptionStatusesInProject
from src.api.router import APIStatuses
from src.config import logger

from src.utils.jwt_utils import decode_jwt

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


class TestStatues(HTTPExceptionStatusesInProject, APIStatuses):
    success: int = 200
    created: int = 201
    unprocessable_entity: int = 422


class Endpoints:
    register = "/users/register"
    login = "/users/login"
    refresh = "/users/refresh"
    me = "users/me"
    profile = "/users/profile"
    subscribe = "/users/subscribe"
    unsubscribe = "/users/unsubscribe"


async def get_token(async_client: "AsyncClient", user_data: dict) -> str:
    response: "Response" = await async_client.post(endpoints.login, data=user_data)

    assert response.status_code == 200
    token: dict = response.json()
    return token["access_token"]


@pytest.fixture(scope="function", autouse=False)
async def token_smile(async_client: "AsyncClient") -> str:
    return await get_token(async_client, {"username": "smile", "password": "12345678"})


@pytest.fixture(scope="function", autouse=False)
async def token_sugar(async_client: "AsyncClient") -> str:
    return await get_token(async_client, {"username": "sugar", "password": "12345678"})


statuses = TestStatues()
endpoints = Endpoints()


@pytest.mark.parametrize(
    "username, email, password, status_code",
    [
        ("smile", "smile@example.com", "12345678", statuses.created),
        ("smile", "sugar@example.com", "12345678", statuses.username_already_exists),
        ("sugar", "smile@example.com", "12345678", statuses.email_already_exists),
        ("sugar", "sugar@example.com", "12345", statuses.weak_password),
        ("", "sugar@example.com", "12345678", statuses.unprocessable_entity),
        ("smile123", "invalid-email", "12345678", statuses.unprocessable_entity),
        ("sugar", "sugar@example.com", "", statuses.unprocessable_entity),
        ("sugar", "sugar@example.com", "12345678", statuses.created),
    ]
)
async def test_register(
        async_client: "AsyncClient", username: str, email: str, password: str, status_code: int
) -> None:
    user_data: dict = {"username": username, "email": email, "password": password}
    response: "Response" = await async_client.post(endpoints.register, data=user_data)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "username, password, status_code, expect_cookies",
    [
        ("smile", "incorrect_password", statuses.unauthorized, False),
        ("incorrect_username", "12345678", statuses.unauthorized, False),
        ("smile", "12345678", statuses.success, True)
    ]
)
async def test_login(
        async_client: "AsyncClient", username, password, status_code, expect_cookies: bool
) -> None:
    login_data: dict = {"username": username, "password": password}
    response: "Response" = await async_client.post(endpoints.login, data=login_data)

    assert response.status_code == status_code
    assert ("jwt_refresh" in response.cookies) == expect_cookies


async def test_refresh(
        async_client: "AsyncClient"
) -> None:
    response: "Response" = await async_client.post(endpoints.refresh)
    response_token: dict = response.json()
    access_token: str = response_token["access_token"]
    assert response.status_code == statuses.created
    assert response_token["access_token"]

    decoded: dict = decode_jwt(access_token)
    assert isinstance(decoded, dict)
    assert decoded["type"] == "access"
    assert decoded["sub"] == 1
    assert decoded["username"] == "smile"
    assert decoded["profile_image"] is None
    assert decoded["role_id"] == 1


class TestMe:
    async def test_with_token(
            self, async_client: "AsyncClient", token_smile: str
    ) -> None:
        headers: dict = {"Authorization": f"Bearer {token_smile}"}
        response: "Response" = await async_client.get(endpoints.me, headers=headers)
        expected_result: dict = {
            "id": 1,
            "username": "smile",
            "email": "smile@example.com",
            "profile_image": None
        }
        assert response.status_code == statuses.success
        assert response.json() == expected_result

    async def test_without_token(
            self, async_client: "AsyncClient"
    ) -> None:
        response: "Response" = await async_client.get(endpoints.me)
        assert response.status_code == statuses.unauthorized


class TestProfile:
    smile_profile_public: dict = {
        "id": 1, "username": "smile", "profile_image": None,
        "followers_count": 0, "followings_count": 0
    }
    smile_profile_private = smile_profile_public

    sugar_profile_public: dict = {
        "id": 2, "username": "sugar", "profile_image": None,
        "followers_count": 0, "followings_count": 0
    }
    sugar_profile_private = sugar_profile_public

    async def test_without_token(self, async_client: "AsyncClient") -> None:
        query_parameters: dict = {"username": "smile"}
        response: "Response" = await async_client.get(endpoints.profile, params=query_parameters)
        assert response.status_code == statuses.public_profile_status_code
        assert response.json() == self.smile_profile_public

    @pytest.mark.parametrize(
        "username, expected_status, expected_result",
        [
            ("smile", statuses.private_profile_status_code, smile_profile_private),
            ("sugar", statuses.public_profile_status_code, sugar_profile_public),
            ("UndefinedUsername", statuses.user_not_exists, None)
        ]
    )
    async def test_with_token(
            self, async_client: "AsyncClient", token_smile: str,
            username: str, expected_status: int, expected_result: dict
    ) -> None:
        query_parameters: dict = {"username": username}
        headers: dict = {"Authorization": f"Bearer {token_smile}"}
        response: "Response" = await async_client.get(
            url=endpoints.profile, params=query_parameters, headers=headers
        )
        assert response.status_code == expected_status
        if expected_result:
            assert response.json() == expected_result


class TestSubscribe:
    async def test_without_token(self, async_client: "AsyncClient") -> None:
        query_params: dict = {"artist_id": 1}
        response: "Response" = await async_client.post(endpoints.subscribe, params=query_params)
        assert response.status_code == statuses.unauthorized

    @pytest.mark.parametrize(
        "user_id, expected_status", [
            (2, statuses.success),
            (3, statuses.user_not_exists),
        ]
    )
    async def test_with_token(
            self, async_client: "AsyncClient", token_smile: str, user_id, expected_status,
    ) -> None:
        headers: dict = {"Authorization": f"Bearer {token_smile}"}
        data: dict = {"artist_id": user_id}
        response: "Response" = await async_client.post(
            endpoints.subscribe, json=data, headers=headers
        )
        assert response.status_code == expected_status

        response_sugar: "Response" = await async_client.get(
            endpoints.profile, params={"username": "sugar"}
        )
        response_smile: "Response" = await async_client.get(
            endpoints.profile, params={"username": "smile"}
        )
        profile_sugar = response_sugar.json()
        profile_smile = response_smile.json()

        assert profile_sugar["followers_count"] == 1
        assert profile_smile["followings_count"] == 1


class TestUnsubscribe:
    async def test_without_token(self, async_client: "AsyncClient") -> None:
        body: dict = {"artist_id": 1}
        response: "Response" = await async_client.post(endpoints.unsubscribe, json=body)
        assert response.status_code == statuses.unauthorized

    @pytest.mark.parametrize(
        "user_id, expected_status, expected_result", [
            (2, statuses.success, True),
            (2, statuses.success, False),
            (3, statuses.success, False),
        ]
    )
    async def test_with_token(
            self, async_client: "AsyncClient", token_smile: str,
            user_id: str, expected_status: int, expected_result: bool
    ) -> None:
        body: dict = {"artist_id": user_id}
        headers: dict = {"Authorization": f"Bearer {token_smile}"}
        response: "Response" = await async_client.post(
            url=endpoints.unsubscribe, json=body, headers=headers
        )
        assert response.status_code == expected_status
        assert response.json() == expected_result
