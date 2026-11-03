from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import select
from gem_service.models import Gem


class GemRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, gem_id: int) -> Gem | None:
        gem = self.session.get(Gem, gem_id)
        if gem is None:
            return None
        return gem

    def get_all(self) -> list[Gem]:
        gems = self.session.scalars(select(Gem)).all()
        return gems

    def create(self, name, price, stock: int = 0):
        gem = Gem(name=name, price=price, stock=stock)

        self.session.add(gem)
        self.session.flush()

        return gem

    def update(
            self,
            gem_id: int,
            name: str,
            price: Decimal,
            stock: int
    ) -> Gem | None:

        gem = self.get_by_id(gem_id)

        if gem is None:
            return None

        gem.name = name
        gem.price = price
        gem.stock = stock
        self.session.flush()

        return gem

    def delete(self, gem_id: int) -> bool:
        gem = self.get_by_id(gem_id)
        if gem is None:
            return False
        self.session.delete(gem)
        self.session.flush()
        return True




