from fastapi import HTTPException


class UsernameAlreadyExistHTTPError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400,
                         detail="User with this username already exists")


class EmailAlreadyExistsHTTPError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400,
                         detail="User with this email already exists")


