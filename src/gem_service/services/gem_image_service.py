import uuid

from gem_service.dto import GemImageDTO
from gem_service.exceptions import (
    GemNotFoundError,
    GemPermissionDeniedError,
    ImageAlreadyExistsError,
    ImageNotFoundError,
    ImageTooLargeError,
    IncorrectTypeError,
)
from gem_service.repositories.gem_image_repository import GemImageRepository
from gem_service.repositories.repositories import GemRepository
from gem_service.storage.s3 import S3Storage


class GemImageService:
    def __init__(
        self,
        gem_repository: GemRepository,
        image_repository: GemImageRepository,
        storage: S3Storage,
    ) -> None:
        self.gem_repository = gem_repository
        self.storage = storage
        self.image_repository = image_repository

    async def create_upload(
        self, gem_id: int, content_type: str, actor_id: uuid.UUID, actor_role: str
    ) -> dict:
        gem = await self.gem_repository.get_by_id(gem_id)
        if gem is None:
            raise GemNotFoundError(f"Gem {gem_id} not found")
        if actor_id != gem.owner_id and actor_role != "admin":
            raise GemPermissionDeniedError("Permission denied")
        if content_type not in ("image/png", "image/jpeg", "image/webp"):
            raise IncorrectTypeError(f"Incorrect content type: {content_type}")
        key = self.storage.generate_object_key(gem_id, content_type[5:])
        upload_data = self.storage.generate_upload_url(key, content_type)
        return {"object_key": key, **upload_data}

    async def confirm_upload(
        self, gem_id: int, object_key: str, actor_id: uuid.UUID, actor_role: str
    ) -> GemImageDTO:
        gem = await self.gem_repository.get_by_id(gem_id)
        if gem is None:
            raise GemNotFoundError(f"Gem {gem_id} not found")
        if actor_id != gem.owner_id and actor_role != "admin":
            raise GemPermissionDeniedError("Permission denied")
        if not object_key.startswith(f"gems/{gem_id}/"):
            raise GemPermissionDeniedError(f"Invalid object key: {object_key}")
        existing_image = await self.image_repository.get_by_object_key(object_key)
        if existing_image is not None:
            if existing_image.gem_id != gem_id:
                raise ImageAlreadyExistsError("Image already exists")
            return existing_image
        metadata = await self.storage.get_object_metadata(object_key)
        if metadata is None:
            raise ImageNotFoundError("Image not found")

        content_type = metadata.get("ContentType")
        if content_type not in ("image/png", "image/jpeg", "image/webp"):
            raise IncorrectTypeError(f"Incorrect content type: {content_type}")

        max_size = 5 * 1024 * 1024
        file_size = metadata.get("ContentLength")
        if not isinstance(file_size, int) or not 0 < file_size <= max_size:
            raise ImageTooLargeError("Invalid image file size")

        image = await self.image_repository.create(gem_id, object_key, content_type)
        await self.image_repository.commit()
        return image
