import uuid
from decimal import Decimal

from gem_service.dto import GemDTO
from gem_service.exceptions import (
    GemAlreadyExistsError,
    GemNotFoundError,
    GemPermissionDeniedError,
    IncorrectPriceError,
)
from gem_service.repositories.outbox_repository import OutboxRepository
from gem_service.repositories.repositories import GemRepository


class GemService:
    def __init__(
        self, repository: GemRepository, outbox_repository: OutboxRepository
    ) -> None:
        self.repository = repository
        self.outbox_repository = outbox_repository

    async def create_gem(
        self,
        name: str,
        price: Decimal,
        owner_id: uuid.UUID,
        stock: int = 0,
    ) -> GemDTO:
        exists = await self.repository.get_by_name(name)

        if exists is not None:
            raise GemAlreadyExistsError("Gem already exists")

        if price <= 0:
            raise ValueError("Price must be greater than 0")

        gem = await self.repository.create(
            name=name, price=price, stock=stock, owner_id=owner_id
        )
        await self.outbox_repository.create(
            event_type="gem_created",
            payload={"gem_id": gem.id, "name": gem.name, "price": str(gem.price)},
        )

        await self.repository.commit()

        return gem

    async def get_gem(self, gem_id: int) -> GemDTO:
        gem = await self.repository.get_by_id(gem_id)

        if gem is None:
            raise GemNotFoundError(f"Gem {gem_id} not found")

        return gem

    async def get_all_gems(self) -> list[GemDTO]:
        return await self.repository.get_all()

    async def update_gem(
        self,
        gem_id: int,
        name: str,
        price: Decimal,
        stock: int,
        actor_id: uuid.UUID,
        actor_role: str,
    ) -> GemDTO:
        gem = await self.repository.get_by_id_for_update(gem_id)

        if gem is None:
            raise GemNotFoundError(f"Gem {gem_id} not found")

        if actor_role != "admin" and actor_id != gem.owner_id:
            raise GemPermissionDeniedError("Permission denied")

        if price <= 0:
            raise IncorrectPriceError("Price must be greater than 0")

        updated_gem = await self.repository.update(
            gem_id, name=name, price=price, stock=stock
        )

        await self.repository.commit()

        return updated_gem

    async def delete_gem(
        self, gem_id: int, actor_id: uuid.UUID, actor_role: str
    ) -> None:
        gem = await self.repository.get_by_id_for_update(gem_id)

        if gem is None:
            raise GemNotFoundError(f"Gem {gem_id} not found")

        if actor_role != "admin" and actor_id != gem.owner_id:
            raise GemPermissionDeniedError("Permission denied")

        await self.repository.delete(gem_id)

        await self.repository.commit()
