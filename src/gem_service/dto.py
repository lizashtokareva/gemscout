import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class GemDTO:
    id: int
    name: str
    price: Decimal
    stock: int
    created_at: datetime
    updated_at: datetime
    owner_id: uuid.UUID


@dataclass(frozen=True)
class IdempotencyRecordDTO:
    id: int
    user_id: uuid.UUID
    key: uuid.UUID
    response_status: int
    response_body: dict
    created_at: datetime
    request_hash: str
