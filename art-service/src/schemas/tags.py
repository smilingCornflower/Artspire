from schemas.base import BaseEntity, CustomBaseModel


class TagEntity(BaseEntity):
    id: int
    name: str


class TagCreateDTO(CustomBaseModel):
    name: str
