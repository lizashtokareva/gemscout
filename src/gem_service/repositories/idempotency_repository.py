import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gem_service.dto import IdempotencyRecordDTO
from gem_service.exceptions import IdempotencyRecordNotFoundError
from gem_service.models import IdempotencyRecord


def to_dto(idempotency: IdempotencyRecord) -> IdempotencyRecordDTO:
    return IdempotencyRecordDTO(
        id=idempotency.id,
        user_id=idempotency.user_id,
        request_hash=idempotency.request_hash,
        created_at=idempotency.created_at,
        key=idempotency.key,
        response_body=idempotency.response_body,
        response_status=idempotency.response_status,
    )


class IdempotencyRepository:
    def __init__(self, session: AsyncSession) -> None:

        self.session = session

    async def get_by_user_and_key(
        self,
        user_id: uuid.UUID,
        key: uuid.UUID,
    ) -> IdempotencyRecordDTO | None:
        stmt = select(IdempotencyRecord).where(
            IdempotencyRecord.user_id == user_id, IdempotencyRecord.key == key
        )
        idempotency = await self.session.scalar(stmt)

        if idempotency is None:
            return None

        return to_dto(idempotency)

    async def create(
        self,
        user_id: uuid.UUID,
        key: uuid.UUID,
        request_hash: str,
    ) -> IdempotencyRecordDTO:
        idempotency = IdempotencyRecord(
            user_id=user_id, key=key, request_hash=request_hash
        )
        self.session.add(idempotency)
        await self.session.flush()

        return to_dto(idempotency)

    async def save_response(
        self,
        record_id: int,
        response_status: int,
        response_body: dict,
    ) -> IdempotencyRecordDTO:
        idempotency = await self.session.get(IdempotencyRecord, record_id)

        if idempotency is None:
            raise IdempotencyRecordNotFoundError(
                f"Idempotency record {record_id} not found"
            )

        idempotency.response_status = response_status
        idempotency.response_body = response_body

        await self.session.flush()
        return to_dto(idempotency)
