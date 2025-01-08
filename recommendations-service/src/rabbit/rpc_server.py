from typing import TYPE_CHECKING
from aio_pika import connect, Message
from aio_pika.exceptions import AMQPException
from config import settings, logger

import asyncio

if TYPE_CHECKING:
    from aio_pika.abc import (
        AbstractConnection,
        AbstractChannel,
        AbstractExchange,
        AbstractQueue,
        AbstractIncomingMessage
    )


class RmqRpcServer:
    def __init__(self, queue_name: str):
        self.queue_name: str = queue_name
        self.connection: "AbstractConnection" | None = None
        self.channel: "AbstractChannel" | None = None
        self.queue: "AbstractQueue" | None = None
        self.exchange: "AbstractExchange" | None = None

    async def connect(self):
        while True:
            try:
                self.connection = await connect(
                    url=settings.rmq.get_connection_url(),
                    client_properties={
                        "heartbeat": settings.rmq.heartbeat,
                        "expiration": str(settings.rmq.timeout_seconds * 1000)
                    }
                )
                self.channel = await self.connection.channel()
                self.queue = await self.channel.declare_queue(name=self.queue_name)
                self.exchange = self.channel.default_exchange
                break
            except AMQPException as err:
                logger.critical(f"Critical error during RabbitMQ connection: {err}", exc_info=True)
                await asyncio.sleep(5)

    async def msg_handler(self, message_body: str) -> str:
        return message_body

    async def process_messages(self):
        try:
            async with self.queue.iterator() as q_iterator:
                async for message in q_iterator:
                    message: "AbstractIncomingMessage"
                    async with message.process():
                        assert message.reply_to is not None
                        message_body: str = message.body.decode()
                        logger.debug(f"message_body = {message_body}")
                        response: str = await self.msg_handler(message_body)

                        await self.exchange.publish(
                            Message(
                                body=response.encode(),
                                correlation_id=message.correlation_id,
                            ),
                            routing_key=message.reply_to
                        )
                        logger.info(f"Sent response")
        except AMQPException as err:
            logger.critical(f"Error: {err}", exc_info=True)
        except Exception as err:
            logger.critical(f"Unexpected error during message processing: {err}", exc_info=True)
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        if self.channel:
            await self.channel.close()
            logger.info("Channel closed.")
        if self.connection:
            await self.connection.close()
            logger.info("Connection closed.")
