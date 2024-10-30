from pathlib import Path

import pika
import sys
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

auth_dir: Path = Path(__file__).parent.parent
env_file: Path = auth_dir / "secrets/.env"


class RMQConfig(BaseModel):
    user: str
    password: str
    host: str
    port: int = 5672
    prefetch_count: int = 50

    heartbeat: int = 120
    timeout_seconds: int = 15

    def get_connection_url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        case_sensitive=False,
        env_nested_delimiter="__"
    )
    mode: str

    rmq: RMQConfig
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
    jwt_access_token_expire_minutes: int = 5
    jwt_refresh_token_expire_minutes: int = 30 * 24 * 60

    logs_path: Path = auth_dir / "logs/debug.log"

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }

    private_profile_status_code: int = 227
    public_profile_status_code: int = 228


settings = Settings()


def custom_record(record):
    record["path"] = f"{record["module"]}/{record["file"]}"
    record["func"] = f"{record["function"]}[{record["line"]}]"
    return record


logger.remove()

logger_format = "<blue>{path:>40}</>::<green>{func:<25}</> || <level>{level:<8}</> || {message}"
logger.configure(patcher=custom_record)

logger.add(sys.stdout, format=logger_format, colorize=True)
