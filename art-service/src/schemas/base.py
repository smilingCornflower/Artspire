from pydantic import BaseModel, ConfigDict


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        from_attributes=True,
    )