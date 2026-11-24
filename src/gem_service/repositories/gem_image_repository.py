from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gem_service.dto import GemImageDTO
from gem_service.models import GemImage


def to_dto(gem_image: GemImage) -> GemImageDTO:
    return GemImageDTO(
        id=gem_image.id,
        gem_id=gem_image.gem_id,
        object_key=gem_image.object_key,
        content_type=gem_image.content_type,
        created_at=gem_image.created_at,
    )


class GemImageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, gem_id: int, object_key: str, content_type: str
    ) -> GemImageDTO:
        gem_image = GemImage(
            gem_id=gem_id, object_key=object_key, content_type=content_type
        )
        self.session.add(gem_image)
        await self.session.flush()

        return to_dto(gem_image)

    async def get_by_object_key(self, object_key: str) -> GemImageDTO | None:
        stmt = select(GemImage).where(GemImage.object_key == object_key)
        gem_image = await self.session.scalar(stmt)

        if gem_image is None:
            return None

        return to_dto(gem_image)

    async def commit(self) -> None:
        await self.session.commit()
