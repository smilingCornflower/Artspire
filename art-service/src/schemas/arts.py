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

    def to_dict(self) -> dict:
        result: dict = {
            "user_id": self.user_id,
            "title": self.title,
            "tags": self.tags,
            "url": self.url,
            "blob_name": self.blob_name,
            "url_generated_at": self.url_generated_at,
        }
        return result