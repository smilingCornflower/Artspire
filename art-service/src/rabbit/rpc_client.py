from typing import TYPE_CHECKING

import asyncio
import uuid
from aio_pika import connect, Message
from aio_pika.exceptions import AMQPException

from config import logger, settings

if TYPE_CHECKING:
    from aio_pika.abc import (
        AbstractQueue,
        AbstractChannel,
        AbstractConnection,
        AbstractIncomingMessage
    )
    from typing import Self, Any


class RmqRpcClient:
    connection: "AbstractConnection"
    channel: "AbstractChannel"
    callback_queue: "AbstractQueue"

    def __init__(self):
        self.correlation_id = None
        self.future = asyncio.Future()

    async def connect(self) -> "Self":
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
    try:
        async with RmqRpcClient() as client:
            logger.info(f"In async with RmqRpcClient() as client:")
            response = await client.call(call_body=body, routing_key=routing_key)
        return response
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        raise e