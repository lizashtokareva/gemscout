import asyncio
import logging

from aio_pika.abc import AbstractExchange

from gem_service.broker.publisher import (
    create_exchange,
    create_rabbitmq_connection,
    publish_event,
)
from gem_service.database import AsyncSessionLocal
from gem_service.repositories.outbox_repository import OutboxRepository

logger = logging.getLogger(__name__)


async def process_outbox_batch(exchange: AbstractExchange) -> int:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            repository = OutboxRepository(session)
            events = await repository.get_unpublished_batch(limit=10)
            for event in events:
                await publish_event(exchange, event)
                await repository.mark_as_published(event)
            return len(events)


async def run_outbox_worker() -> None:
    connection = await create_rabbitmq_connection()
    try:
        exchange = await create_exchange(connection)
        while True:
            try:
                processed = await process_outbox_batch(exchange)
            except Exception as e:
                logger.exception(e)
                await asyncio.sleep(5)
            else:
                if processed == 0:
                    await asyncio.sleep(1)
    finally:
        await connection.close()
