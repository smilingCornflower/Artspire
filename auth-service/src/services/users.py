from repositories.repository import AbstractRepository
from schemas.users import UserCreateSchema
from utils.password import hash_password


from exceptions.http import (
    UsernameAlreadyExistHTTPException,
    EmailAlreadyExistsHTTPException,
    WeakPasswordHTTPException,
)


class UserService:
    def __init__(self, user_repo: AbstractRepository):
        self.user_repo = user_repo

    async def add_user(self, user_create_data: UserCreateSchema) -> int:
        user_by_username = await self.user_repo.find_all(filter_by={"username": user_create_data.username})
        if user_by_username:
            raise UsernameAlreadyExistHTTPException

        user_by_email = await self.user_repo.find_all(filter_by={"email": user_create_data.email})
        if user_by_email:
            raise EmailAlreadyExistsHTTPException

        if len(user_create_data.password) < 6:
            raise WeakPasswordHTTPException

        hashed_password = hash_password(password=user_create_data.password)

        new_user_data: dict = {
            "username": user_create_data.username,
            "email": user_create_data.email,
            "hashed_password": hashed_password,
        }
        new_user_id: int = await self.user_repo.add_one(data=new_user_data)

        return new_user_id
