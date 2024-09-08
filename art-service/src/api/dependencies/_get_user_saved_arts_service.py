from repositories.user_saved_arts import UserSavedArtsRepository
from services.user_saved_arts import UserSavedArtsService


def get_user_saved_arts_service() -> "UserSavedArtsService":
    return UserSavedArtsService(UserSavedArtsRepository())
