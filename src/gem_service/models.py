import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.sqlite import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Gem(Base):
    __tablename__ = "gems"

    __table_args__ = (
        CheckConstraint("price > 0", name="ck_gems_price_positive"),
        CheckConstraint("stock >= 0", name="ck_gems_stock_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    stock: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"Gem(id={self.id}, name={self.name}, created_at={self.created_at})"


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "key",
            name="uq_idempotency_user_key",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    key: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    request_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    response_status: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    response_body: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class GemImage(Base):
    __tablename__ = "gem_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    gem_id: Mapped[int] = mapped_column(
        ForeignKey("gems.id"), nullable=False, index=True
    )
    object_key: Mapped[str] = mapped_column(String(1024), unique=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
