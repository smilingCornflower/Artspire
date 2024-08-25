from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path

auth_dir: Path = Path(__file__).parent.parent
env_file: Path = auth_dir / "secrets/.env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        case_sensitive=False,
    )
    db_user: str
    db_host: str
    db_port: str
    db_pass: str
    db_name: str

    db_echo: bool = False
    db_echo_pool: bool = False
    db_pool_size: int = 50
    db_max_overflow: int = 10

    @property
    def db_url(self):
        url: str = f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"
        return url

    jwt_private_key_path: Path = auth_dir / "secrets/jwt-private.pem"
    jwt_public_key_path: Path = auth_dir / "secrets/jwt-public.pem"
    jwt_access_token_expire_minutes: int = 30

    logs_path: Path = auth_dir / "logs/debug.log"

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }


settings = Settings()