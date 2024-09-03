from pydantic import BaseModel
from datetime import datetime


class ArtUploadSchema(BaseModel):
    user_id: int
    title: str | None
    tags: list[str]


class ArtCreateSchema(BaseModel):
    user_id: int
    title: str | None
    tags: list[str]
    url: str
    blob_name: str
    url_generated_at: datetime