from fastapi import HTTPException, status


class FailedUploadHttpException(HTTPException):
    def __init__(self, detail: str = "Failed to upload file"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class InvalidImageTypeHTTPException(HTTPException):
    def __init__(self, detail: str = "Invalid image type provided"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class InternalServerErrorHTTPException(HTTPException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class UnauthorizedHTTPException(HTTPException):
    def __init__(self, detail: str = "User unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class ForbiddenHTTPException(HTTPException):
    def __init__(self, detail: str = "Action forbidden: Moderators and Admins only"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class ArtNotFoundHTTPException(HTTPException):
    def __init__(self, detail: str = "Art not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class TagAlreadyExistsHTTPException(HTTPException):
    def __init__(self, detail: str = "Tag already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class ArtAlreadySavedHTTPException(HTTPException):
    def __init__(self, detail: str = "Art already saved"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class CommentLengthHTTPException(HTTPException):
    def __init__(self, detail: str = "Comment length should be more than 0 and less than 512"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class InvalidRandomSeedHTTPException(HTTPException):
    def __init__(self, detail: str = "Random seed must be float and between -1.0 and 1.0"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
