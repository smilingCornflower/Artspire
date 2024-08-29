import asyncio
import uuid

from aio_pika import connect, Message
from aio_pika.exceptions import AMQPException
from abc import ABC
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
    connection: "AbstractConnection"
    channel: "AbstractChannel"
    callback_queue: "AbstractQueue"

    def __init__(self):
        self.correlation_id = None
        self.future = asyncio.Future()

    async def connect(self) -> "Self":
        try:
            logger.info("Connecting to RabbitMQ...")
            self.connection = await connect(url=settings.rmq.get_connection_url())
            self.channel = await self.connection.channel()
            self.callback_queue = await self.channel.declare_queue(exclusive=True)
            await self.callback_queue.consume(callback=self.on_response)
            logger.info("Connected and queue declared successfully.")
            return self
        except AMQPException as err:
            logger.critical(f"AMQP error during RabbitMQ connection: {err}", exc_info=True)

            raise

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
                    reply_to=self.callback_queue.name,
                ),
                routing_key=routing_key,
            )
            response = await self.future
            logger.debug(f"Received response: {response}")
            return response
        except AMQPException as err:
            logger.error(f"AMQP error during message publish: {err}", exc_info=True)
            raise


async def run_rpc_client(body: str, routing_key: str) -> "Any":
    client = RmqRpcClient()
    try:
        await client.connect()
        response = await client.call(call_body=body, routing_key=routing_key)
        return response
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        raise e