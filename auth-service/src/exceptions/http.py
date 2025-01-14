from fastapi import HTTPException, status
from config import settings


class HTTPExceptionStatusesInProject:
    MAX_USERNAME_SIZE: int = settings.username_size

    username_already_exists: int = 452
    username_too_long: int = 455

    email_already_exists: int = 453
    weak_password: int = status.HTTP_400_BAD_REQUEST
    inter_server_error: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    user_not_active: int = status.HTTP_403_FORBIDDEN
    unauthorized: int = status.HTTP_401_UNAUTHORIZED
    invalid_token: int = status.HTTP_401_UNAUTHORIZED
    failed_to_subscribe: int = 454
    user_not_exists: int = status.HTTP_404_NOT_FOUND


statuses = HTTPExceptionStatusesInProject()


class UsernameAlreadyExistHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=statuses.username_already_exists,
                         detail="User with this username already exists")


class UsernameTooLongHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=statuses.username_too_long,
                         detail=f"Username must not exceed {statuses.MAX_USERNAME_SIZE} characters.")


class EmailAlreadyExistsHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=statuses.email_already_exists,
                         detail="User with this email already exists")


class WeakPasswordHTTPException(HTTPException):
    def __init__(self, detail: str = "Password is too weak"):
        super().__init__(status_code=statuses.weak_password,
                         detail=detail)


class InternalServerHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=statuses.inter_server_error,
                         detail="Something went wrong on server")


class UserNotActiveHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=statuses.user_not_active,
                         detail="User is not active")


class UnauthorizedHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=statuses.unauthorized,
                         detail="Invalid username or password")


class InvalidTokenHTTPException(HTTPException):
    def __init__(self, status_code: int = statuses.invalid_token,
                 detail: str = "Invalid token received"):
        super().__init__(status_code=status_code,
                         detail=detail)


class InvalidTokenTypeHTTPException(InvalidTokenHTTPException):
    def __init__(self, received_type: str, expected_type: str):
        super().__init__(
            detail=f"Invalid token type: {received_type}, expected: {expected_type}"
        )


class FailedToSubscribeHTTPException(HTTPException):
    def __init__(self, detail: str = "Failed to process subscription request"):
        super().__init__(status_code=statuses.failed_to_subscribe,
                         detail=detail)


class UserNotExistsHTTPException(HTTPException):
    def __init__(self, detail: str = "User does not exists"):
        super().__init__(status_code=statuses.user_not_exists,
                         detail=detail)


class UserNotFoundHTTPException(HTTPException):
    def __init__(self, status_code: int = status.HTTP_404_NOT_FOUND,
                 detail: str = "User Not Found"):
        super().__init__(status_code=status_code, detail=detail)


class InvalidImageTypeHTTPException(HTTPException):
    def __init__(self, detail: str = "Invalid image type provided"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
