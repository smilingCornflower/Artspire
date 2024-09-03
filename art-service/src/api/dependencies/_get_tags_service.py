from services.tags import TagsService
from repositories.tags import TagRepository


def get_tags_service() -> "TagsService":
    return TagsService(TagRepository())
