from decimal import Decimal

from gem_service.exceptions import GemAlreadyExistsError, GemNotFoundError
from gem_service.models import Gem
from gem_service.repositories.repositories import GemRepository


class GemService:
    def __init__(self, repository: GemRepository) -> None:
        self.repository = repository

    async def create_gem(self, name: str, price: Decimal, stock: int = 0) -> Gem:
        exists = await self.repository.get_by_name(name)

        if exists is not None:
            raise GemAlreadyExistsError("Gem already exists")

        gem = await self.repository.create(name=name, price=price, stock=stock)
        return gem

    async def get_gem(self, gem_id: int) -> Gem:
        gem = await self.repository.get_by_id(gem_id)

        if gem is None:
            raise GemNotFoundError(f"Gem {gem_id} not found")

        return gem

    async def get_all_gems(self) -> list[Gem]:
        return await self.repository.get_all()

    async def update_gem(
        self, gem_id: int, name: str, price: Decimal, stock: int
    ) -> Gem:
        gem = await self.repository.get_by_id(gem_id)

        if gem is None:
            raise GemNotFoundError(f"Gem {gem_id} not found")

        updated_gem = await self.repository.update(
            gem_id, name=name, price=price, stock=stock
        )
        return updated_gem

    async def delete_gem(self, gem_id: int) -> None:
        gem = await self.repository.get_by_id(gem_id)

        if gem is None:
            raise GemNotFoundError(f"Gem {gem_id} not found")

        await self.repository.delete(gem_id)
