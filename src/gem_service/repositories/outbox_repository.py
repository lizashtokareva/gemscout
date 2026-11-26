from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gem_service.models import OutboxEvent


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, event_type: str, payload: dict) -> None:
        event = OutboxEvent(event_type=event_type, payload=payload)
        self.session.add(event)
        await self.session.flush()

    async def get_unpublished_batch(self, limit: int = 10) -> list[OutboxEvent]:
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def mark_as_published(self, event: OutboxEvent) -> None:
        event.published_at = datetime.now(timezone.utc)
        await self.session.flush()
