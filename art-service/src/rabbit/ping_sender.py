import aio_pika
from config import settings, logger
import asyncio
from aio_pika.abc import AbstractConnection, AbstractChannel


async def ping_sender():
    try:
        logger.info("Connecting to RabbitMQ...")
        connection: AbstractConnection = await aio_pika.connect(url=settings.rmq.get_connection_url())
        channel: AbstractChannel = await connection.channel()
        logger.info("Connection established and channel opened.")

        while True:
            try:
                logger.info("Sending ping message...")
                await channel.default_exchange.publish(
                    message=aio_pika.Message(
                        body='ping'.encode()
                    ),
                    routing_key='ping_queue',
                )
                logger.info("Ping")
            except Exception as e:
                logger.error(f"Error sending message: {e}")

            await asyncio.sleep(120)

    except Exception as e:
        logger.critical(f"Error during connection or channel initialization: {e}")

if __name__ == "__main__":
    asyncio.run(ping_sender())