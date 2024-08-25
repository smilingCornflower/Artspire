from pydantic import BaseModel


class AccessTokenInfoSchema(BaseModel):
    access_token: str
    token_type: str

