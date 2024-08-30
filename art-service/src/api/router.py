from typing import TYPE_CHECKING
from fastapi import APIRouter, Depends, UploadFile
from fastapi.security.http import HTTPBearer
from .dependencies.get_user_data import get_user_data
from .dependencies.get_art_service import get_art_service
from exceptions.http_exc import UnauthorizedHTTPException, FailedUploadHttpException
from schemas.arts import ArtUploadSchema
from schemas.entities import UserEntity
if TYPE_CHECKING:
    from fastapi.security.http import HTTPAuthorizationCredentials
    from services.arts import ArtsService

from rabbit.jwt_client import run_jwt_client

router = APIRouter(
    prefix="/arts",
    tags=["Arts"],
)


@router.post("")
async def post_art(
        art_file: UploadFile,
        art_tags: str,
        art_title: str | None,
        art_service: "ArtsService" = Depends(get_art_service),
        user_data: "UserEntity" = Depends(get_user_data),
) -> int:
    art_upload_data: "ArtUploadSchema" = ArtUploadSchema(
        user_id=user_data.id,
        title=art_title,
        tags=art_tags.split(","),
    )
    try:
        new_art_id: int = await art_service.add_art(art_data=art_upload_data, art_file=art_file)
    except FailedUploadHttpException as err:
        raise
    return new_art_id