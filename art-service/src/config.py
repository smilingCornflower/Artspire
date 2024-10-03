from pathlib import Path
from datetime import date
import sys
import pika
from loguru import logger
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

art_dir: Path = Path(__file__).parent.parent
env_file: Path = art_dir / "secrets/.env"


class DatabaseConfig(BaseModel):
    user: str
    host: str
    port: str
    password: str
    name: str

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    def get_db_url(self) -> str:
        url: str = (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        )
        return url

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class BucketConfig(BaseModel):
    credentials_path: Path = art_dir / "secrets/bucket-credentials.json"
    bucket_name: str = "artspire-bucket"
    expiration_days: int = 7


class RMQConfig(BaseModel):
    host: str
    port: int = 5672
    user: str
    password: str
    prefetch_count: int = 50
    timeout_seconds: int = 10

    def get_connection_url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"


class LoggingConfig(BaseModel):
    today_date: str = str(date.today())
    info_logs_path: Path = art_dir / f"logs/{today_date}/info.log"
    debug_logs_path: Path = art_dir / f"logs/{today_date}/debug.log"
    warning_logs_path: Path = art_dir / f"logs/{today_date}/warning.log"
    error_logs_path: Path = art_dir / f"logs/{today_date}/error.log"
    critical_logs_path: Path = art_dir / f"logs/{today_date}/critical.log"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    db: DatabaseConfig
    rmq: RMQConfig
    s3: BucketConfig = BucketConfig()
    log: LoggingConfig = LoggingConfig()


settings = Settings()

logger.remove()

logger_format = (
    "<green>{file:>25}</>/<blue>{function:<25}</> || "
    "<level>{level:<8}</> || <cyan><{line}></>: {message}"
)

logger.add(sys.stdout, format=logger_format, colorize=True)
