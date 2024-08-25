from sqlalchemy.exc import SQLAlchemyError


class UserNotFoundSQLError(SQLAlchemyError):
    def __init__(self, message: str = "User not found in the database"):
        super().__init__(message)
