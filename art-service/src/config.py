from pathlib import Path
from datetime import date
import sys
import pika
import os
from loguru import logger
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

art_dir: Path = Path(__file__).parent.parent
src_dir: Path = art_dir / "src"
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
    heartbeat: int = 120

    def get_connection_url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"


class LoggingConfig(BaseModel):
    today_date: str = str(date.today())
    info_logs_path: Path = art_dir / f"logs/{today_date}/info.log"
    debug_logs_path: Path = art_dir / f"logs/{today_date}/debug.log"
    warning_logs_path: Path = art_dir / f"logs/{today_date}/warning.log"
    error_logs_path: Path = art_dir / f"logs/{today_date}/error.log"
    critical_logs_path: Path = art_dir / f"logs/{today_date}/critical.log"


class Server(BaseModel):
    host: str
    auth_port: int
    arts_port: int


class ProjectStatusCodes:
    success: int = 1000
    json_decode_error: int = 1001
    img_invalid_type_error: int = 1002
    os_error: int = 1003
    google_cloud_error: int = 1004


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    mode: str
    db: DatabaseConfig
    rmq: RMQConfig
    server: Server
    s3: BucketConfig = BucketConfig()
    log: LoggingConfig = LoggingConfig()
    project_statuses: ProjectStatusCodes = ProjectStatusCodes()


settings = Settings()


def custom_record(record):
    record["path"] = f"{record["module"]}/{record["file"]}"
    record["func"] = f"{record["function"]}[{record["line"]}]"
    return record


logger.remove()

logger_format = "<blue>{path:>40}</>::<green>{func:<25}</> || <level>{level:<8}</> || {message}"
logger.configure(patcher=custom_record)

logger.add(sys.stdout, format=logger_format, colorize=True, level="DEBUG")
