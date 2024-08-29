from pydantic import BaseModel


class BaseEntity(BaseModel):
    id: int
