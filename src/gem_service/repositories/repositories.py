from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from gem_service.models import Gem


class GemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, gem_id: int) -> Gem | None:
        gem = await self.session.get(Gem, gem_id)
        if gem is None:
            return None
        return gem

    async def get_all(self) -> list[Gem]:
        result = await self.session.scalars(select(Gem))
        gems = result.all()
        return gems

    async def create(self, name, price, stock: int = 0) -> Gem:
        gem = Gem(name=name, price=price, stock=stock)

        self.session.add(gem)
        await self.session.flush()

        return gem

    async def update(
            self,
            gem_id: int,
            name: str,
            price: Decimal,
            stock: int
    ) -> Gem | None:

        gem = await self.get_by_id(gem_id)

        if gem is None:
            return None

        gem.name = name
        gem.price = price
        gem.stock = stock
        gem.updated_at = datetime.now()
        await self.session.flush()

        return gem

    async def delete(self, gem_id: int) -> bool:
        gem = self.get_by_id(gem_id)
        if gem is None:
            return False
        await self.session.delete(gem)
        await self.session.flush()
        return True

    async def get_by_name(self, name: str) -> Gem | None:
        return await self.session.scalar(
            select(Gem).where(Gem.name == name)
        )


    async def get_expensive_gems(self) -> list[Gem]:
        result = await self.session.scalars(select(Gem).where(Gem.price > 1000).order_by(Gem.price))
        return result.all()



