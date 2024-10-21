from pydantic import BaseModel, ConfigDict


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        from_attributes=True,
    )


class BaseEntity(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        from_attributes=True,
        extra="forbid",
        strict=True,
    )

