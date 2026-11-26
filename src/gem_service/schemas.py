import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class GemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0)
    stock: int = Field(default=0, ge=0)


class GemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    stock: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CurrentUser:
    id: uuid.UUID
    role: str


class GemImageUploadRequest(BaseModel):
    content_type: str


class ConfirmImageUploadRequest(BaseModel):
    object_key: str


class GemCreatedEvent(BaseModel):
    gem_id: int
    name: str
    price: Decimal
