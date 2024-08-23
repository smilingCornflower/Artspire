from fastapi import APIRouter
from fastapi.responses import JSONResponse

from database import db_manager
from models import UserOrm
from schemas import UserCreateSchema
from service import create_user_in_db

from exc import UsernameAlreadyExistError, EamilAlreadyExistsError


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post("/register")
async def create_new_user(
        user: UserCreateSchema
) -> JSONResponse:
    try:
        new_user: UserOrm = await create_user_in_db(user=user)
    except (UsernameAlreadyExistError, EamilAlreadyExistsError) as err:
        raise
    return JSONResponse(content=f"User created successfully!")
