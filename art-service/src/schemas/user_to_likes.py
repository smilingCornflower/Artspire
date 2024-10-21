from schemas.base import BaseEntity, CustomBaseModel


class UsersToLikesEntity(BaseEntity):
    user_id: int
    art_id: int


class UsersToLikesCreateDTO(CustomBaseModel):
    user_id: int
    art_id: int
