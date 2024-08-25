from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError


class UsernameAlreadyExistHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="User with this username already exists")


class EmailAlreadyExistsHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="User with this email already exists")


class WeakPasswordHTTPException(HTTPException):
    def __init__(self, detail: str = "Password is too weak"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=detail)


class InterServerHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail="Something went wrong on server")


class UnauthorizedHTTPException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password")