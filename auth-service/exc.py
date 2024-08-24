from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError


class UsernameAlreadyExistHTTPError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="User with this username already exists")


class EmailAlreadyExistsHTTPError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="User with this email already exists")


class WeakPasswordHTTPError(HTTPException):
    def __init__(self, detail: str = "Password is too weak"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=detail)


class InterServerHTTPError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail="Something went wrong on server")


class UnauthorizedHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password")


class UserNotFoundSQLError(SQLAlchemyError):
    def __init__(self, message: str = "User not found in the database"):
        super().__init__(message)
