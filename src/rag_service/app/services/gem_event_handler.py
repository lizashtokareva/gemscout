import asyncio

from gem_service.schemas import GemCreatedEvent
from rag_service.broker.consumer import logger


async def handle_gem_created(event: GemCreatedEvent) -> None:
    logger.info(
        "New gem: id=%s, name=%s, price=%s", event.gem_id, event.name, event.price
    )


async def process_with_retries(event: GemCreatedEvent) -> None:
    for attempt in range(3):
        try:
            await handle_gem_created(event)
            return

        except Exception:
            if attempt == 2:
                raise

            await asyncio.sleep(2**attempt)
