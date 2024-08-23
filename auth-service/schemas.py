from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

