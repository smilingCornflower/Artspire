import bcrypt


# Максимальная длина для корректной работы это 72 символа
def hash_password(
        password: str
) -> str:
    salt: bytes = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    hashed_pwd: bytes = bcrypt.hashpw(password=pwd_bytes,
                                      salt=salt)
    hashed_pwd: str = hashed_pwd.decode()
    return hashed_pwd


def check_password(
        password: str,
        hashed_password: str,
) -> bool:
    hashed_password: bytes = hashed_password.encode()
    result: bool = bcrypt.checkpw(password=password.encode(),
                                  hashed_password=hashed_password)
    return result
