import asyncio
import logging

import aio_pika
from aio_pika.abc import AbstractRobustChannel, AbstractRobustQueue
from pydantic import ValidationError

from gem_service.schemas import GemCreatedEvent
from rag_service.app.core.config import settings
from rag_service.app.services.gem_event_handler import process_with_retries

logger = logging.getLogger(__name__)


async def setup_gem_events_queue(channel: AbstractRobustChannel) -> AbstractRobustQueue:
    dead_exchange = await channel.declare_exchange(
        "gem.dlx", aio_pika.ExchangeType.DIRECT, durable=True
    )
    dead_queue = await channel.declare_queue("rag.gem.events.dlq", durable=True)
    await dead_queue.bind(dead_exchange, routing_key="gem.failed")
    exchange = await channel.declare_exchange(
        "gem.events", aio_pika.ExchangeType.TOPIC, durable=True
    )
    queue = await channel.declare_queue(
        "rag.gem.events",
        durable=True,
        arguments={
            "x-dead-letter-exchange": "gem.dlx",
            "x-dead-letter-routing-key": "gem.failed",
        },
    )
    await queue.bind(exchange, routing_key="gem.created")
    return queue


async def consume_gem_events(queue: AbstractRobustQueue) -> None:
    async with queue.iterator() as iterator:
        async for message in iterator:
            try:
                event_id = message.message_id

                if event_id is None:
                    raise ValueError("Missing message_id")
                payload = GemCreatedEvent.model_validate_json(message.body)

            except (ValueError, ValidationError):
                logger.info("Received event %s: %s", event_id, payload)
                await message.reject(requeue=False)
                continue
            try:
                await process_with_retries(payload)

            except Exception:
                logger.exception("Failed to process message")
                await message.reject(requeue=False)

            else:
                await message.ack()


async def run_consumer() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=5)
        queue = await setup_gem_events_queue(channel)
        await consume_gem_events(queue)
    await channel.close()


if __name__ == "__main__":
    asyncio.run(run_consumer())
