import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gem_service.dto import GemDTO
from gem_service.exceptions import GemNotFoundError
from gem_service.models import Gem


def to_dto(gem: Gem) -> GemDTO:
    return GemDTO(
        id=gem.id,
        name=gem.name,
        price=gem.price,
        stock=gem.stock,
        created_at=gem.created_at,
        updated_at=gem.updated_at,
        owner_id=gem.owner_id,
    )


class GemRepository:
    def __init__(self, session: AsyncSession) -> None:

        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def get_by_id(self, gem_id: int) -> GemDTO | None:
        gem = await self.session.get(Gem, gem_id)
        if gem is None:
            return None

        return to_dto(gem)

    async def get_by_id_for_update(
        self,
        gem_id: int,
    ) -> GemDTO | None:
        stmt = select(Gem).where(Gem.id == gem_id).with_for_update()
        gem = await self.session.scalar(stmt)

        if gem is None:
            return None

        return to_dto(gem)

    async def get_all(self) -> list[GemDTO]:
        result = await self.session.scalars(select(Gem))
        gems = result.all()
        gem_dtos = [to_dto(gem) for gem in gems]
        return gem_dtos

    async def create(
        self,
        name: str,
        price: Decimal,
        owner_id: uuid.UUID,
        stock: int = 0,
    ) -> GemDTO:
        gem = Gem(name=name, price=price, stock=stock, owner_id=owner_id)

        self.session.add(gem)
        await self.session.flush()

        return to_dto(gem)

    async def update(
        self, gem_id: int, name: str, price: Decimal, stock: int
    ) -> GemDTO:

        gem = await self.session.get(Gem, gem_id)

        if gem is None:
            raise GemNotFoundError

        gem.name = name
        gem.price = price
        gem.stock = stock
        gem.updated_at = datetime.now()

        await self.session.flush()

        return to_dto(gem)

    async def delete(self, gem_id: int) -> bool:
        gem = await self.session.get(Gem, gem_id)
        if gem is None:
            return False
        await self.session.delete(gem)
        await self.session.flush()
        return True

    async def get_by_name(self, name: str) -> GemDTO | None:
        gem = await self.session.scalar(select(Gem).where(Gem.name == name))

        if gem is None:
            return None

        return to_dto(gem)

    async def get_expensive_gems(self) -> list[GemDTO]:
        gems = await self.session.scalars(
            select(Gem).where(Gem.price > 1000).order_by(Gem.price)
        )
        return [to_dto(gem) for gem in gems]
