import asyncio
from config import settings, logger
from aio_pika import connect, Message
from typing import TYPE_CHECKING
from abc import ABC
from aio_pika.exceptions import AMQPException

if TYPE_CHECKING:
    from aio_pika.abc import (
        AbstractConnection,
        AbstractChannel,
        AbstractExchange,
        AbstractQueue,
        AbstractIncomingMessage,
    )


class RmqRpcServer:
    def __init__(self, queue_name: str):
        self.queue_name: str = queue_name
        self.connection: "AbstractConnection" = None
        self.channel: "AbstractChannel" = None
        self.exchange: "AbstractExchange" = None
        self.queue: "AbstractQueue" = None

    async def connect(self):
        while True:
            try:
                logger.info("Connecting to RabbitMQ...")
                self.connection = await connect(
                    url=settings.rmq.get_connection_url(),
                    client_properties={"heartbeat": 120}
                )
                self.channel = await self.connection.channel()
                self.exchange = self.channel.default_exchange
                self.queue = await self.channel.declare_queue(name=self.queue_name)
                logger.info("Connected to RabbitMQ and queue declared successfully.")
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
                    async with message.process(requeue=False):
                        assert message.reply_to is not None
                        msg_body: str = message.body.decode()
                        logger.debug(f"Received message: {msg_body}")

                        response: str = await self.msg_handler(msg_body)

                        await self.exchange.publish(
                            Message(
                                body=response.encode(),
                                correlation_id=message.correlation_id,
                            ),
                            routing_key=message.reply_to,
                        )
                        logger.debug(f"Sent response: {response.encode()}")
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
