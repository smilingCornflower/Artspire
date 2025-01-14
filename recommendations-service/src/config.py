from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from loguru import logger
from pathlib import Path
import sys

rec_dir: Path = Path(__file__).parent.parent
env_file: Path = rec_dir / "secret/.env"


class Database(BaseModel):
    user: str
    host: str
    password: str
    name: str
    port: int

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    def get_db_url(self) -> str:
        url: str = (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        )
        return url


class RedisExpire(BaseModel):
    art_ids: int = 60 * 10


class Paths(BaseModel):
    arts_csr: Path = rec_dir / "src/data/arts_csr_matrix.npz"
    arts_sim_matrix: Path = rec_dir / "src/data/arts_similarity_matrix.npy"
    art_indices_to_ids: Path = rec_dir / "src/data/art_indices_to_ids.pkl"
    art_ids_to_indices: Path = rec_dir / "src/data/art_ids_to_indices.pkl"

    cft_model: Path = rec_dir / "src/data/ft_cc.en.300_freqprune_100K_20K_pq_100.bin"
    pca_model: Path = rec_dir / "src/data/pca_en_300_to_100D_model.joblib"


class Arts(BaseModel):
    max_tags: int = 20


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
        env_nested_delimiter="__",
    )
    db: Database
    rmq: RMQConfig
    arts: Arts = Arts()
    paths: Paths = Paths()
    redis_ex: RedisExpire = RedisExpire()

    update_password: str


settings = Settings()


def custom_record(record):
    record["path"] = f"{record["module"]}/{record["file"]}"
    record["func"] = f"{record["function"]}[{record["line"]}]"
    return record


logger.remove()

logger_format = "<blue>{path:>40}</>::<green>{func:<40}</> || <level>{level:<8}</> || {message}"
logger.configure(patcher=custom_record)

logger.add(sys.stdout, format=logger_format, colorize=True)
