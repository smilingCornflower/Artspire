import asyncio
import uuid

from aio_pika import connect, Message
from aio_pika.exceptions import AMQPException
from abc import ABC

import config
from config import settings, logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aio_pika.abc import (
        AbstractQueue,
        AbstractChannel,
        AbstractExchange,
        AbstractConnection,
        AbstractIncomingMessage
    )
    from typing import MutableMapping, Self, Any


class RmqRpcClient:
    """
    A base class for implementing an asynchronous RabbitMQ RPC client with aio-pika.

    Core features:
      - Establishes a connection and declares a dedicated callback queue.
      - Publishes messages with a correlation ID.
      - Waits for a response with the matching correlation ID in `on_response`.
    """
    connection: "AbstractConnection"
    channel: "AbstractChannel"
    callback_queue: "AbstractQueue"

    def __init__(self):
        """
        Initializes the client and sets up an asyncio.Future to hold the server response.
        """
        self.correlation_id = None
        self.future = asyncio.Future()

    async def connect(self) -> "Self":
        """
        Creates a connection, channel, and an exclusive queue to receive responses.
        Subscribes `on_response` to the callback queue.

        :return: The RmqRpcClient instance (allows chaining).
        :raises AMQPException: On connection or queue declaration errors.
        """
        try:
            logger.info("Connecting to RabbitMQ...")
            self.connection = await connect(
                url=settings.rmq.get_connection_url(),
                client_properties={
                    "expiration": str(settings.rmq.timeout_seconds * 1000),
                }
            )
            self.channel = await self.connection.channel()
            self.callback_queue = await self.channel.declare_queue(exclusive=True)
            await self.callback_queue.consume(callback=self.on_response)
            logger.info("Connected and queue declared successfully.")
            return self
        except AMQPException as err:
            logger.critical(f"AMQP error during RabbitMQ connection: {err}", exc_info=True)

            raise

    async def close(self):
        try:
            if not self.connection.is_closed:
                await self.channel.close()
                await self.connection.close()
                logger.info("Connection to RabbitMQ closed.")
        except AMQPException as err:
            logger.error(f"Error while closing connection: {err}", exc_info=True)
            raise

    async def __aenter__(self) -> "Self":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def on_response(self, message: "AbstractIncomingMessage") -> None:
        """
        Compares the incoming message's correlation_id with the client's current correlation_id.
        If they match, the message is acknowledged and the response is set on the Future.

        :param message: An incoming RabbitMQ message.
        :raises AMQPException: If acknowledging the message fails.
        """
        try:
            logger.debug(f"Received message with correlation_id: {message.correlation_id}")
            if message.correlation_id == self.correlation_id:
                await message.ack()
                response_body = message.body.decode()
                logger.debug(f"Response message: {response_body}")
                self.future.set_result(response_body)
            else:
                logger.warning(f"Received message with mismatched correlation_id: {message.correlation_id}")
        except AMQPException as err:
            logger.error(f"AMQP error processing message: {err}", exc_info=True)
            raise

    async def call(self, call_body: str, routing_key: str):
        """
        Publishes a message (with a unique correlation_id) to the specified routing key
        and waits for the response in `self.future`.

        :param call_body: The content of the message (usually JSON-encoded).
        :param routing_key: The RabbitMQ routing key or queue name.
        :return: The server's response body as a string.
        :raises AMQPException: If there's an error during publishing or receiving the response.
        """
        try:
            self.correlation_id = str(uuid.uuid4())
            logger.debug(f"Publishing message with correlation_id: {self.correlation_id}")

            await self.channel.default_exchange.publish(
                Message(
                    body=call_body.encode(),
                    correlation_id=self.correlation_id,
                    reply_to=self.callback_queue.name
                ),
                routing_key=routing_key,
            )
            response = await self.future
            return response
        except AMQPException as err:
            logger.error(f"AMQP error during message publish: {err}", exc_info=True)
            raise


async def run_rpc_client(body: str, routing_key: str) -> "Any":
    """
    Sends a message to a RabbitMQ routing key and awaits a response.

    :param body: JSON-encoded string to send.
    :param routing_key: The RabbitMQ routing key.
    :return: The raw response from the server.
    """
    async with RmqRpcClient() as client:
        logger.info(f"In async with RmqRpcClient() as client:")
        response = await client.call(call_body=body, routing_key=routing_key)
    return response
