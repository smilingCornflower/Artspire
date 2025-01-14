import base64

from fastapi import Response, UploadFile

from config import logger, settings
from exceptions.http import (EmailAlreadyExistsHTTPException, UnauthorizedHTTPException,
                             UsernameAlreadyExistHTTPException, UsernameTooLongHTTPException,
                             UserNotActiveHTTPException, UserNotFoundHTTPException,
                             WeakPasswordHTTPException)
from rabbit.s3_client import run_s3_add_client, run_s3_get_client
from repositories.users import UserRepository
from schemas.rabbit_ import S3AddSchema, S3GetSchema
from schemas.tokens import AccessTokenSchema, TokenInfoSchema
from schemas.users import (UserCreateSchema, UserEntity, UserLoginSchema, UserProfilePrivate,
                           UserProfilePublic)
from utils.jwt_utils import create_access_jwt, create_refresh_jwt
from utils.password import check_password, hash_password
from utils.set_httponly import set_refresh_in_httponly


def create_token_for_user(user: UserEntity, include_refresh: bool = True) -> TokenInfoSchema:
    access_payload: dict = {
        "sub": user.id,
        "username": user.username,
        "email": user.email,
        "profile_image": user.profile_image,
        "role_id": user.role_id,
    }
    refresh_payload: dict = {
        "sub": user.id,
    }

    access_token: str = create_access_jwt(token_data=access_payload)
    refresh_token: str = create_refresh_jwt(token_data=refresh_payload)

    if include_refresh:
        token_info: TokenInfoSchema = TokenInfoSchema(access_token=access_token,
                                                      refresh_token=refresh_token)
    else:
        token_info: TokenInfoSchema = TokenInfoSchema(access_token=access_token)
    return token_info


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def _validate_username(self, username: str) -> None:
        user_by_username: list[UserEntity] = await self.user_repo.find_all(
            filter_by={"username": username})

        if user_by_username:
            logger.warning(f"Username '{username}' already exists.")
            raise UsernameAlreadyExistHTTPException

        if len(username) > settings.username_size:
            raise UsernameTooLongHTTPException

    async def add_user(self, user_create_data: UserCreateSchema) -> int:
        user_by_email = await self.user_repo.find_all(filter_by={"email": user_create_data.email})
        await self._validate_username(user_create_data.username)

        if user_by_email:
            logger.warning(f"Email '{user_create_data.email}' already exists.")
            raise EmailAlreadyExistsHTTPException

        if len(user_create_data.password) < settings.password_size:
            logger.warning("Provided password is too weak.")
            raise WeakPasswordHTTPException

        hashed_password = hash_password(password=user_create_data.password)
        new_user_data: dict = {
            "username": user_create_data.username,
            "email": user_create_data.email,
            "hashed_password": hashed_password,
        }
        new_user_id: int = await self.user_repo.add_one(data=new_user_data)
        logger.info(f"User '{user_create_data.username}' added with ID: {new_user_id}")
        return new_user_id

    async def validate_user(self, response: Response, user: UserLoginSchema) -> AccessTokenSchema:

        user_by_username: list[UserEntity] = await self.user_repo.find_all(
            {"username": user.username})

        if not user_by_username:
            logger.warning(f"Unauthorized access attempt for username: '{user.username}'")
            raise UnauthorizedHTTPException

        if not user_by_username[0].is_active:
            logger.warning(f"User '{user.username}' is not active.")
            raise UserNotActiveHTTPException

        user_entity: UserEntity = user_by_username[0]
        correct_password: str = user_entity.hashed_password
        check_password_result: bool = check_password(user.password, correct_password)

        if not check_password_result:
            logger.warning(f"Incorrect password attempt for user: '{user.username}'")
            raise UnauthorizedHTTPException

        token_data: TokenInfoSchema = create_token_for_user(user=user_entity)

        set_refresh_in_httponly(response=response, refresh_token=token_data.refresh_token)
        access_toke_data: AccessTokenSchema = AccessTokenSchema.model_validate(token_data)

        logger.info(f"Token created for user '{user.username}'")
        return access_toke_data

    async def create_token_for_user_by_id(self, user_id: int,
                                          include_refresh: bool = False) -> TokenInfoSchema:
        user_by_id: list[UserEntity] = await self.user_repo.find_all({"id": user_id})
        result_token = create_token_for_user(
            user=user_by_id[0],
            include_refresh=include_refresh)
        logger.info(f"Token created for user ID: {user_id}")
        return result_token

    async def get_all_users(self, users_id: list[int]):
        result_users: list[UserEntity] = await self.user_repo.find_all({"id": users_id})
        users_info: list[dict] = []
        for user in result_users:
            user_info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "profile_image": user.profile_image,
            }
            users_info.append(user_info)
        logger.info(f"Retrieved information for {len(users_info)} users.")
        return users_info

    async def get_profile_by_username(self, username: str,
                                      private: bool = False) -> "UserProfilePrivate | UserProfilePublic":
        logger.info(f"Retrieving profile for username: {username}, private view: {private}")

        result_users: list[UserEntity] = await self.user_repo.find_all({"username": username})

        if not result_users:
            logger.warning(f"User '{username}' not found")
            raise UserNotFoundHTTPException(detail="User with such username not found")

        user = result_users[0]
        logger.info(f"User '{username}' found")
        if private:
            user_profile = UserProfilePrivate.model_validate(user)
        else:
            user_profile = UserProfilePublic.model_validate(user)

        logger.debug(f"Profile data for user '{username}': {user_profile}")

        return user_profile

    async def change_username(self, user_id: int, new_username: str) -> None:
        await self._validate_username(new_username)
        await self.user_repo.update_one(model_id=user_id, data={"username": new_username})

    async def set_profile_picture(self, user_id: int, image: UploadFile) -> None:
        """
        Sets or updates the user's profile picture.

        Steps:
        1. Reads the uploaded file as bytes.
        2. Base64-encodes the image data.
        3. Constructs an S3AddSchema object containing the encoded image, MIME type, and blob name.
        4. Calls run_s3_add_client(...) to store the image in external storage.
        5. Updates the user's profile in the repository with the resulting blob name.

        :param user_id: The ID of the user whose profile picture is being updated.
        :param image: The uploaded file containing the user's new profile picture.
        :raises InterServerHTTPException: If the storage operation fails or returns a non-successful status.
        Note: The InternalServerException might be raised by the run_s3_add_client function, not directly by set_profile_picture.
        """
        img_bytes: bytes = await image.read()
        img_type: str = image.content_type
        logger.debug(f"img_type: {img_type}")

        img_base64: bytes = base64.b64encode(img_bytes)
        img_base64: str = img_base64.decode("utf-8")

        img_blob_name: str = f"profile_pictures/user_{user_id}.jpg"
        logger.debug(f"img_blob_name: {img_blob_name}")

        img_add_data = S3AddSchema(img_base64=img_base64,
                                   img_type=img_type,
                                   blob_name=img_blob_name)

        img_blob_name: str = await run_s3_add_client(body=img_add_data)
        await self.user_repo.update_one(model_id=user_id, data={"profile_image": img_blob_name})

    async def get_profile_picture(self, user_id: int) -> str:
        """
        Retrieves the URL for a user's profile picture by their ID.

        Steps:
          1. Looks up the user in the repository based on the provided `user_id`.
          2. Extracts the `profile_image` field (blob name) from the user's record if found.
          3. Constructs an `S3GetSchema` object and invokes `run_s3_get_client` to get the image URL.
          4. Returns the obtained URL as a string.

        :param user_id: int — The ID of the user whose profile picture is being retrieved.
        :return: str — A string containing the URL of the user's profile picture.
        :raises UserNotFoundHTTPException: If no user with the specified `user_id` exists in the database.
        """
        user_by_id: list[UserEntity] = await self.user_repo.find_all({"id": user_id})
        if user_by_id:
            user_entity: UserEntity = user_by_id[0]
            img_blob_name: str = user_entity.profile_image
            logger.debug(f"img_blob_name = {img_blob_name}")
        else:
            logger.critical(f"User with id = {user_id} not found in the database")
            raise UserNotFoundHTTPException

        msg_body = S3GetSchema(blob_name=img_blob_name)
        logger.info(f"msg_body = {msg_body}")

        img_url: str = await run_s3_get_client(body=msg_body)
        return img_url
