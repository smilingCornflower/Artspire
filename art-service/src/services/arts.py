# Standard libraries
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
import uuid
from typing import TYPE_CHECKING

# External libraries
import shortuuid
from google.cloud.exceptions import GoogleCloudError
from sqlalchemy.exc import SQLAlchemyError

# Local modules
from bucket.s3_service import s3_service
from rabbit.users_client import run_users_client
from config import logger
from exceptions.http_exc import (
    ArtNotFoundHTTPException,
    InternalServerErrorHTTPException,
)

from schemas.arts import (
    ArtCreateDTO, ArtPostSchema, ArtEntity, ArtGetResponseShort, ArtGetResponseFull
)

if TYPE_CHECKING:
    from fastapi import UploadFile
    from repositories.arts import ArtRepository
    from repositories.art_to_tag import ArtToTagRepository
    from repositories.tags import TagRepository
    from repositories.users_to_likes import UsersToLikesRepository
    from schemas.entities import UsersToLikesEntity, UserEntity
    from schemas.tags import TagEntity


class BaseArtsService:
    def __init__(
            self,
            art_repo: "ArtRepository",
            art_to_tag_repo: "ArtToTagRepository",
            tag_repo: "TagRepository",
            user_to_likes_repo: "UsersToLikesRepository",
    ) -> None:
        self.art_repo = art_repo
        self.art_to_tag_repo = art_to_tag_repo
        self.tag_repo = tag_repo
        self.user_to_likes_repo = user_to_likes_repo


class ArtsGetService(BaseArtsService):
    SIX_DAYS_IN_SECONDS: int = 6 * 24 * 3600

    async def _refresh_art_url_if_needed(self, art: "ArtEntity") -> "ArtEntity":
        """
        Refresh the art URL if it is older than 6 days.

        This method checks the age of the art URL. If the URL is older than 6 days,
        a new URL is generated and both the URL and the timestamp are updated in the database.

        :param art: The art entity to check and potentially update.
        :return: The updated art entity with a refreshed URL, or the original if no refresh was needed.
        :raises InternalServerErrorHTTPException: If there is an error generating the new URL or updating the database.
        """

        generated_at_dt: datetime = art.url_generated_at
        current_dt: datetime = datetime.now(tz=timezone.utc)
        current_dt: datetime = current_dt.replace(tzinfo=None)
        # With tzinfo it raises exceptions, IDK why, just don't touch it.

        dt_diff_in_seconds: float = (current_dt - generated_at_dt).total_seconds()
        if dt_diff_in_seconds > self.SIX_DAYS_IN_SECONDS:
            try:
                art_new_url: str = s3_service.create_url(art.blob_name)
            except GoogleCloudError as err:
                logger.error("Error: {err}")
                raise InternalServerErrorHTTPException from err
            to_refresh: dict = {
                "url": art_new_url,
                "url_generated_at": current_dt,
            }
            new_art: "ArtEntity" = art.model_copy()
            new_art.url = art_new_url
            new_art.url_generated_at = current_dt
            try:
                await self.art_repo.update_one(model_id=art.id, data=to_refresh)
            except SQLAlchemyError as err:
                logger.critical("Error: {err}")
                logger.debug(f"model_id: {art.id}; to_refresh: {to_refresh}")
                raise InternalServerErrorHTTPException from err
            return new_art
        return art

    async def _refresh_arts_url_if_needed(self, arts: list["ArtEntity"]) -> list["ArtEntity"]:
        """
        Refresh URLs for a list of art entities if they are outdated.

        Iterates through the given list of arts, checking each for URL expiration
        and refreshing them as needed.

        :param arts: A list of art entities to check and refresh.
        :return: A list of updated art entities.
        """
        logger.info(f"STARTED _refresh_arts_url_if_needed")
        result: "list[ArtEntity]" = []
        for art in arts:
            refreshed_art: "ArtEntity" = await self._refresh_art_url_if_needed(art)
            result.append(refreshed_art)
        return result

    async def _increase_views_count(self, art_id: int | None) -> None:
        """
        Increment the view count of a specific art by 1.

        :param art_id: The ID of the art to increment the view count for.
        """
        if art_id:
            await self.art_repo.change_counter(art_id, number=1, counter_name="views")

    async def _get_liked_arts_for_user(self, user_id: int | None) -> set[int]:
        """
        Retrieve the IDs of arts liked by a specific user.

        :param user_id: The ID of the user to retrieve liked arts for.
        :return: A set of IDs of arts liked by the user.
        """
        if not user_id:
            return set()
        # noinspection PyTypeChecker
        result_likes: "list[UsersToLikesEntity]" = await self.user_to_likes_repo.find_all(
            filter_by={"user_id": user_id}
        )
        result_arts_id: set[int] = {i.art_id for i in result_likes}
        return result_arts_id

    async def _get_prepared_out_arts(
            self, arts: list["ArtEntity"], user_id: int, is_one_art: bool
    ) -> "list[ArtGetResponseShort | ArtGetResponseFull]":
        """
        Prepare the output format for a list of arts, with like status.

        Converts a list of art entities into their corresponding schema,
        and marks each one as liked or not based on the provided set of liked art IDs.

        :param arts: The list of art entities to convert.
        :param user_id: The ID of the user for whom the liked arts are being searched.
        :param is_one_art: A flag indicating if a single art is being processed.
        :return: A list of art schemas, either short or full format.
        """
        liked_arts: set = await self._get_liked_arts_for_user(user_id=user_id)
        if is_one_art:
            art_entity: "ArtEntity" = arts[0]
            user: dict[int, "UserEntity"] = await run_users_client(users_id=[art_entity.user_id])
            user: "UserEntity" = user[art_entity.user_id]

            art_out_data: dict = {
                **art_entity.model_dump(),
                "username": user.username,
                "profile_image": user.profile_image,
                "is_liked": art_entity.id in liked_arts,
            }
            art_out_full_info: ArtGetResponseFull = ArtGetResponseFull.model_validate(art_out_data)
            result: list = [art_out_full_info]
        else:
            result: "list[ArtGetResponseShort]" = []
            for entity in arts:
                entity: "ArtEntity"
                art_out_short_info: "ArtGetResponseShort" = ArtGetResponseShort.model_validate(entity)
                art_out_short_info.is_liked = art_out_short_info.id in liked_arts
                result.append(art_out_short_info)
        return result

    async def get_arts(
            self,
            art_id: int | None = None,
            offset: int | None = None,
            limit: int | None = None,
            include_likes_for_user_id: int | None = None,
    ) -> list:
        """
        Retrieve arts from the database with optional filtering, pagination, and additional options.

        If `art_id` is provided, retrieves the art with that specific ID.
        Otherwise, retrieves all arts with optional pagination and tag inclusion.
        If the URLs of the arts are outdated, they are refreshed.
        Optionally retrieves the like status of the arts for a specific user.

        :param art_id: The ID of a specific art to retrieve, or None to retrieve all arts.
        :param offset: The number of arts to skip for pagination.
        :param limit: The maximum number of arts to retrieve.
        :param include_tags: Whether to include associated tags for each art.
        :return: A list of art schemas, either in short or full format depending on the request.
        :raises ArtNotFoundHTTPException: If no arts are found.
        :raises InternalServerErrorHTTPException: If an error occurs in the database operation.
        """
        logger.warning(f"Started get_arts()")
        try:
            if art_id:
                filter_condition: dict = {"id": art_id}
                art_attributes: list | None = ["tags"]
            else:
                filter_condition: dict = {}
                art_attributes: list | None = None
            # noinspection PyTypeChecker
            all_arts: list["ArtEntity"] = await self.art_repo.find_all(
                filter_by=filter_condition,
                offset=offset,
                limit=limit,
                joined_attributes=art_attributes)
            if not all_arts:
                raise ArtNotFoundHTTPException(detail="No art found")
        except SQLAlchemyError as err:
            logger.critical(f"Error: {err}")
            logger.debug(
                f"art_id: {art_id}; offset: {offset}; limit: {limit}"
                f" include_likes_for_user_id: {include_likes_for_user_id}"
            )
            raise InternalServerErrorHTTPException from err

        all_arts: list["ArtEntity"] = await self._refresh_arts_url_if_needed(arts=all_arts)
        result: "list[ArtGetResponseShort | ArtGetResponseFull]" = await self._get_prepared_out_arts(
            arts=all_arts, user_id=include_likes_for_user_id, is_one_art=bool(art_id),
        )
        logger.info(f"Finished get_arts()")
        return result


class ArtsAddRepository(BaseArtsService):
    async def add_art(
            self,
            art_data: "ArtPostSchema",
            create_tags: bool = True,
    ) -> int:
        """
        Add a new art to the repository, with optional tag creation.

        This method handles the process of uploading an image file to S3 storage using
        `s3_service.upload_image()`. If the uploaded file is not a valid image,
        an `InvalidImageTypeHTTPException` is raised.

        After a successful upload, the method generates a URL for accessing the image, stores it
        in the database along with metadata from `art_data`, and returns the ID of the newly
        created art record.

        If `create_tags` is set to True, the method also handles tag creation and association
        of tags with the art. It first checks if the tags already exist, creates any missing
        tags, and links them to the newly created art.

        :param art_data: A data structure containing all necessary information about the art
            being uploaded.
            - user_id (int): The ID of the user uploading the art. This is required for
              associating the art with the user and for naming the file in S3 storage.
            - art_file (UploadFile): The file representing the artwork to be uploaded. This
              file is expected to be an image. If the file is not a valid image, the method will
              raise an `InvalidImageTypeHTTPException`.
            - title (str | None): optional field
            - tags (list[str]): A list of tags associated with the artwork. Each tag represents
              a keyword or category for the art. If `create_tags` is set to True, the method will
              ensure that these tags are created in the system and associated with the uploaded
              artwork. If the list is empty or not provided, no tags will be created or associated.

        :param create_tags: If True, the method will create and associate tags with the art.
            The tags specified in `art_data.tags` will be checked, and any missing tags will be
            created. The newly created tags (or existing ones) will then be linked to the artwork.

        :return: The ID of the newly created art record in the database.

        :raises InvalidImageTypeHTTPException: If the uploaded file is not a valid image.
        :raises InternalServerErrorHTTPException: If an error appears during the database operation.
        """
        logger.warning("STARTED add_art()")
        blob_name: str = await s3_service.upload_image(
            image_file=art_data.art_file, user_id=art_data.user_id
        )
        art_url: str = s3_service.create_url(blob_name=blob_name)
        url_generated_dt: datetime = datetime.now(tz=timezone.utc)
        url_generated_dt: datetime = url_generated_dt.replace(tzinfo=None)

        art_create_dto: "ArtCreateDTO" = ArtCreateDTO(
            user_id=art_data.user_id,
            title=art_data.title,
            url=art_url,
            blob_name=blob_name,
            url_generated_at=url_generated_dt,
        )
        tag_names: list[str] = art_data.tags
        try:
            logger.info(f"await self.art_repo.add_one(art_create_dto.model_dump())")
            new_art_id: int = await self.art_repo.add_one(art_create_dto.model_dump())
            if create_tags:
                tag_names_to_add_data: list[dict] = [
                    {"name": name} for name in tag_names
                ]
                logger.info(
                    f"await self.tag_repo.add_one({tag_names_to_add_data}, ['name'])"
                )
                await self.tag_repo.add_one(
                    data=tag_names_to_add_data, ignore_conflicts=["name"]
                )

            tag_entities: list = await self.tag_repo.find_all({"name": tag_names})
            art_to_tag_add_data: list[dict] = [
                {"art_id": new_art_id, "tag_id": tag_entity.id}
                for tag_entity in tag_entities
            ]
            logger.info(f"await self.art_to_tag_repo.add_one({art_to_tag_add_data}")
            await self.art_to_tag_repo.add_one(art_to_tag_add_data)
        except SQLAlchemyError as err:
            logger.critical(f"Error: {err}")
            raise InternalServerErrorHTTPException from err
        return new_art_id


class ArtsDeleteService(BaseArtsService):
    UNDELETED_BLOB_NAMES_FILE: str = "undeleted_blob_names.txt"

    async def delete_art(self, art_id: int) -> bool:
        """
        Deletes an art by its ID from the database and S3 storage.

        First, checks if the art exists in the database. If found, deletes the art record
        from the database and attempts to delete the associated file from S3 storage.
        If the file deletion fails, the blob name is recorded in the `UNDELETED_BLOB_NAMES_FILE`.

        :param art_id: The ID of the art to be deleted.
        :return: True if the art was deleted, False if the art was not found.
        :raises InternalServerErrorHTTPException: If there is a database error.
        """
        try:
            # noinspection PyTypeChecker
            art_entities: list["ArtEntity"] = await self.art_repo.find_all(
                {"id": art_id}
            )
            if not art_entities:
                return False
        except SQLAlchemyError as err:
            raise InternalServerErrorHTTPException from err

        art_entity: "ArtEntity" = art_entities[0]
        try:
            await self.art_repo.delete_one({"id": art_id})
        except SQLAlchemyError as err:
            logger.error(f"Error: {err}")
            raise InternalServerErrorHTTPException from err
        try:
            s3_service.delete_file(blob_name=art_entity.blob_name)
        except GoogleCloudError as err:
            logger.error(f"Error {err}")
            with open(self.UNDELETED_BLOB_NAMES_FILE, mode="a", encoding="utf-8") as f:
                f.write(f"{art_entity.blob_name}\n")

        return True


class ArtsService(ArtsGetService, ArtsAddRepository, ArtsDeleteService):
    ...
