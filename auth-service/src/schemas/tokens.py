from .base_ import CustomBaseModel


class AccessTokenSchema(CustomBaseModel):
    access_token: str
    token_type: str = "Bearer"


class TokenInfoSchema(AccessTokenSchema):
    refresh_token: str | None = None
