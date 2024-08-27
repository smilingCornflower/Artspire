from typing import TYPE_CHECKING
import aio_pika
from aio_pika import ExchangeType

if TYPE_CHECKING:
    from aio_pika.abc import (
        AbstractChannel,
        AbstractExchange,
        AbstractRobustConnection
    )


class RabbitMQClient:
    def __init__(self, connection_url: str):
        self.connection_url: str = connection_url
        self.connection: "AbstractRobustConnection | None" = None
        self.channel: "AbstractChannel | None" = None
        self.exchange: "AbstractExchange | None" = None

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.connection_url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange("direct_exchange", ExchangeType.DIRECT)

    async def __aenter__(self) -> "RabbitMQClient":
        await self.connect()
        return self

    async def __aexit__(self,
                        exc_type: type | None,
                        exc_val: BaseException | None,
                        exc_tb: BaseException | None
                        ) -> None:
        if self.connection:
            await self.connection.close()

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()
