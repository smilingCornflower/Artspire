from fastapi import HTTPException


class UsernameAlreadyExistHTTPError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400,
                         detail="User with this username already exists")


class EmailAlreadyExistsHTTPError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400,
                         detail="User with this email already exists")


class WeakPasswordHTTPError(HTTPException):
    def __init__(self, detail: str = "Password is too weak"):
        super().__init__(status_code=400,
                         detail=detail)