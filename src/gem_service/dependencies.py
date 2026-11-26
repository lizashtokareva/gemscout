from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from gem_service.database import get_session
from gem_service.repositories.outbox_repository import OutboxRepository
from gem_service.repositories.repositories import GemRepository
from gem_service.services.gem_service import GemService


def get_gem_repository(
    session: AsyncSession = Depends(get_session),
) -> GemRepository:
    return GemRepository(session)


def get_outbox_repository(
    session: AsyncSession = Depends(get_session),
) -> OutboxRepository:
    return OutboxRepository(session)


def get_gem_service(
    gem_repository: GemRepository = Depends(get_gem_repository),
    outbox_repository: OutboxRepository = Depends(get_outbox_repository),
) -> GemService:
    return GemService(gem_repository, outbox_repository)
