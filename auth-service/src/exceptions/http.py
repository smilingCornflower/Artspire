from fastapi import HTTPException, status


class UsernameAlreadyExistHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT,
                         detail="User with this username already exists")


class EmailAlreadyExistsHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT,
                         detail="User with this email already exists")


class WeakPasswordHTTPException(HTTPException):
    def __init__(self, detail: str = "Password is too weak"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=detail)


class InterServerHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail="Something went wrong on server")


class UserNotActiveHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN,
                         detail="User is not active")


class UnauthorizedHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Invalid username or password")


class InvalidTokenHTTPException(HTTPException):
    def __init__(self, status_code: int = status.HTTP_401_UNAUTHORIZED,
                 detail: str = "Invalid token received"):
        super().__init__(status_code=status_code,
                         detail=detail)


class InvalidTokenTypeHTTPException(InvalidTokenHTTPException):
    def __init__(self, received_type: str, expected_type: str):
        super().__init__(
            detail=f"Invalid token type: {received_type}, expected: {expected_type}"
        )
