from typing import Callable
from .client import RabbitMQClient


class RabbitMQConsumer(RabbitMQClient):
    async def consume_messages(self, queue_name: str, routing_key: str, callback: Callable) -> None:
        queue = await self.channel.declare_queue(queue_name, durable=True)
        await queue.bind(self.exchange, routing_key)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await callback(message)