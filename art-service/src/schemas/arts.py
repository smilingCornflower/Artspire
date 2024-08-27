from pydantic import BaseModel


class ArtCreateSchame(BaseModel):
    user_id: int
    title: str | None
    tags: list[str]
