from typing import TYPE_CHECKING
from aio_pika import Message, DeliveryMode
from .client import RabbitMQClient


if TYPE_CHECKING:
    from aio_pika.abc import AbstractMessage

class Producer(RabbitMQClient):
    async def publish_message(self, routing_key: str, message_body: str) -> None:
        message: "AbstractMessage" = Message(
            body=message_body.encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        if self.exchange:
            await self.exchange.publish(message=message, routing_key=routing_key)

    async def get_connection(self) -> "Producer":
        return self
