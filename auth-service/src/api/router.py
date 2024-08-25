from fastapi import APIRouter, Form
from schemas.users import UserCreateSchema
from dependencies import get_user_service


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/register")
async def register_user(
        user_create_schema: UserCreateSchema,
        user_service=Depends(user_service)
) -> int:
    new_user_id: int = await user_service.add_user(user_create_schema)
    return new_user_id

