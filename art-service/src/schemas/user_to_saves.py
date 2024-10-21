from schemas.base import BaseEntity, CustomBaseModel


class UsersToSavesEntity(BaseEntity):
    user_id: int
    art_id: int


class UsersToSavesCreateDTO(CustomBaseModel):
    user_id: int
    art_id: int
