from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings

# Annotation
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from typing import AsyncGenerator

from loguru import logger


logger.add(settings.logs_path,
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{file} | {function} | {line}] \n \t {message}",
           level="DEBUG",
           rotation="10 MB",
           compression="zip"
           )


class DatabaseManager:
    def __init__(self,
                 url: str,
                 echo: bool = False,
                 echo_pool: bool = False,
                 pool_size: int = 5,
                 max_overflow: int = 10,
                 ):
        self.url: str = url
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

    @property
    def async_session_maker(self) -> async_sessionmaker:
        async_session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        return async_session_factory

    async def dispose(self) -> None:
        await self.engine.dispose()


db_manager = DatabaseManager(
    url=settings.db_url,
    echo=settings.db_echo,
    echo_pool=settings.db_echo_pool,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)
