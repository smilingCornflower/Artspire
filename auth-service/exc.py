from fastapi import HTTPException


class UsernameAlreadyExistError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400,
                         detail="User with this username already exists")


class EamilAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400,
                         detail="User with this email already exists")
