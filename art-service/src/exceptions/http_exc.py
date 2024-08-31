from fastapi import HTTPException, status


class FailedUploadHttpException(HTTPException):
    def __init__(self, detail: str = "Failed to upload file"):
        super().__init__(
            status_code=500,
            detail=detail,
        )


class UnauthorizedHTTPException(HTTPException):
    def __init__(self, detail: str = "User unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class InternalServerErrorHTTPException(HTTPException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class ForbiddenHTTPException(HTTPException):
    def __init__(self, detail: str = "Action forbidden: Moderators and Admins only"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
