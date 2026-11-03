from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, func, Numeric, Integer, DateTime, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Gem(Base):
    __tablename__ = 'gems'

    __table_args__ = (CheckConstraint("price > 0", name="ck_gems_price_positive"),
    CheckConstraint("stock >= 0", name="ck_gems_stock_nonnegative"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    stock: Mapped[int] = mapped_column(Integer, default = 0, server_default="0", nullable=False)


    def __repr__(self) -> str:
        return f'Gem(id={self.id}, name={self.name}, created_at={self.created_at})'

