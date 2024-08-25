from pydantic import BaseModel


class TokenInfoSchema(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"

