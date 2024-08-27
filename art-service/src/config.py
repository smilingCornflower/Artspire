from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path
from loguru import logger

art_dir: Path = Path(__file__).parent.parent
env_file: Path = art_dir / "secrets/.env"


class RMQConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 5672
    user: str
    password: str

    def get_connection_url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"


class LoggingConfig(BaseModel):
    info_logs_path: Path = art_dir / "logs/info.log"
    debug_logs_path: Path = art_dir / "logs/debug.log"
    warning_logs_path: Path = art_dir / "logs/warning.log"
    error_logs_path: Path = art_dir / "logs/error.log"
    critical_logs_path: Path = art_dir / "logs/critical.log"


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
        url: str = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        return url

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    db: DatabaseConfig
    rmq: RMQConfig
    log: LoggingConfig = LoggingConfig()


settings = Settings()


def setup_logger(log_path: str | Path, log_level: str):
    logger_format: str = "{level} | {file} | {function} | {line} | {time:YYYY-MM-DD HH:mm:ss} \n\t {message}"
    logger.add(log_path,
               format=logger_format,
               level=log_level,
               rotation="10 MB",
               compression="zip")


setup_logger(log_path=settings.log.debug_logs_path, log_level="DEBUG")
setup_logger(log_path=settings.log.info_logs_path, log_level="INFO")
setup_logger(log_path=settings.log.warning_logs_path, log_level="WARNING")
setup_logger(log_path=settings.log.error_logs_path, log_level="ERROR")
setup_logger(log_path=settings.log.critical_logs_path, log_level="CRITICAL")
