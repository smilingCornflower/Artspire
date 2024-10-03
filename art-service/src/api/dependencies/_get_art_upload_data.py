import logging
from typing import Annotated, TYPE_CHECKING

from fastapi import Depends, Query
from ._get_user_data import get_user_data

from schemas.arts import ArtUploadSchema
from config import logger

if TYPE_CHECKING:
    from schemas.entities import UserEntity

TAGS_REGEX: str = r"^(\w+)+(,\w+)*$"


# Regex to match a string of one or more words separated by commas.
# This regex accepts these entries:
# Tag_123
# Tag1,Tag2
# tag_one,tag_two,tag_three,tag_four


async def get_art_upload_data(
    art_tags: Annotated[
        str, Query(examples=[{"example": "Tag1,Tag2,Tag3,Tag4"}], pattern=TAGS_REGEX)
    ],
    user_data: Annotated["UserEntity", Depends(get_user_data)],
    art_title: str | None = None,
) -> "ArtUploadSchema":
    art_tags_list = art_tags.split(",")
    art_upload_data: "ArtUploadSchema" = ArtUploadSchema(
        user_id=user_data.id,
        title=art_title,
        tags=art_tags_list,
    )
    logger.info(f"Created ArtUploadSchema: {art_upload_data}")

    return art_upload_data
