import json

import aio_pika
from aio_pika.abc import AbstractExchange, AbstractRobustConnection

from gem_service.config import settings
from gem_service.models import OutboxEvent


async def create_rabbitmq_connection() -> AbstractRobustConnection:
    broker_url = settings.rabbitmq_url
    return await aio_pika.connect_robust(broker_url)


async def create_exchange(connection: AbstractRobustConnection) -> AbstractExchange:
    channel = await connection.channel(publisher_confirms=True, on_return_raises=True)
    return await channel.declare_exchange(
        name="gem.events", type=aio_pika.ExchangeType.TOPIC, durable=True
    )


async def publish_event(exchange: AbstractExchange, event: OutboxEvent) -> None:
    message = aio_pika.Message(
        body=json.dumps(event.payload).encode("utf-8"),
        message_id=str(event.id),
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )

    await exchange.publish(message, routing_key=event.event_type, mandatory=True)
