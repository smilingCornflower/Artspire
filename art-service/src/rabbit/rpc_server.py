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
    """
    A base class for creating an asynchronous RabbitMQ RPC server using aio-pika.

    Provides:
      - Automatic connection setup and retry logic.
      - Queue declaration for listening to incoming RPC requests.
      - A message-processing loop that reads from the queue, invokes `msg_handler`,
        and responds to the `reply_to` queue.
    """
    def __init__(self, queue_name: str):
        """
        Sets the queue name to consume messages from.

        :param queue_name: The RabbitMQ queue that this server will consume.
        :type queue_name: str
        """
        self.queue_name: str = queue_name
        self.connection: "AbstractConnection" = None
        self.channel: "AbstractChannel" = None
        self.exchange: "AbstractExchange" = None
        self.queue: "AbstractQueue" = None

    async def connect(self):
        """
        Establishes an asynchronous connection to RabbitMQ, declares a channel and
        the specified queue, and binds them. Retries on connection failure.
        """
        while True:
            try:
                self.connection = await connect(
                    url=settings.rmq.get_connection_url(),
                    client_properties={
                        "heartbeat": settings.rmq.heartbeat,
                        "expiration": str(settings.rmq.timeout_seconds * 1000)}
                )
                self.channel = await self.connection.channel()
                self.exchange = self.channel.default_exchange
                self.queue = await self.channel.declare_queue(name=self.queue_name)
                break
            except AMQPException as err:
                logger.critical(f"Critical error during RabbitMQ connection: {err}", exc_info=True)
                await asyncio.sleep(5)

    async def msg_handler(self, message_body: str) -> str:
        """
        Default handler for incoming messages. Subclasses should override this method
        to process messages and return an appropriate response.

        :param message_body: The body of the message, decoded into a string.
        :return: A response to be sent back to the message sender.
        """
        return message_body

    async def process_messages(self):
        """
        Consumes messages from the queue and processes them in a loop. Each message is:
          - Decoded into a string.
          - Handled by `msg_handler`.
          - Replied to via the `reply_to` property in the original message.

        Cleans up the connection if an error occurs or the loop ends.
        """
        try:
            async with self.queue.iterator() as q_iterator:
                async for message in q_iterator:
                    message: "AbstractIncomingMessage"
                    async with message.process(requeue=False):
                        assert message.reply_to is not None
                        msg_body: str = message.body.decode()
                        logger.info(f"Received message")

                        response: str = await self.msg_handler(msg_body)

                        await self.exchange.publish(
                            Message(
                                body=response.encode(),
                                correlation_id=message.correlation_id,
                            ),
                            routing_key=message.reply_to,
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

    async def __aenter__(self) -> "Self":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await s3_rpc_server.cleanup()
        if exc_type:
            logger.critical(f"Unexpected error occurred: {e}")
            return False
