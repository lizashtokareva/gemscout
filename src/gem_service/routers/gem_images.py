from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from gem_service.database import get_session
from gem_service.dependencies.auth import require_role
from gem_service.dto import GemImageDTO
from gem_service.repositories.gem_image_repository import GemImageRepository
from gem_service.repositories.repositories import GemRepository
from gem_service.routers.gems import get_gem_repository
from gem_service.schemas import (
    ConfirmImageUploadRequest,
    CurrentUser,
    GemImageUploadRequest,
)
from gem_service.services.gem_image_service import GemImageService
from gem_service.storage.s3 import S3Storage

router = APIRouter(prefix="/gems", tags=["Gem Images"])


def get_gem_image_repository(
    session: AsyncSession = Depends(get_session),
) -> GemImageRepository:
    return GemImageRepository(session)


@router.post("/{gem_id}/images/upload-url")
async def create_image_upload(
    gem_id: int,
    image_data: GemImageUploadRequest,
    repo: GemRepository = Depends(get_gem_repository),
    current_user: CurrentUser = Depends(require_role("seller", "admin")),
) -> dict:
    storage = S3Storage()
    service = GemImageService(gem_repository=repo, storage=storage)
    return await service.create_upload(
        gem_id,
        content_type=image_data.content_type,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )


@router.post("/{gem_id}/images/confirm")
async def confirm_upload(
    gem_id: int,
    data: ConfirmImageUploadRequest,
    repository: GemRepository = Depends(get_gem_repository),
    image_repository: GemImageRepository = Depends(get_gem_image_repository),
    current_user: CurrentUser = Depends(require_role("seller", "admin")),
) -> GemImageDTO:
    service = GemImageService(
        gem_repository=repository,
        image_repository=image_repository,
        storage=S3Storage(),
    )
    return await service.confirm_upload(
        gem_id=gem_id,
        object_key=data.object_key,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )
