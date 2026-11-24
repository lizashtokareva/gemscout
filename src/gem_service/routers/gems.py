from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from gem_service.database import get_session
from gem_service.dependencies.auth import require_role
from gem_service.dto import GemDTO
from gem_service.repositories.repositories import GemRepository
from gem_service.schemas import CurrentUser, GemCreate, GemRead
from gem_service.services.gem_service import GemService

router = APIRouter(prefix="/gems", tags=["Gems"])


def get_gem_repository(
    session: AsyncSession = Depends(get_session),
) -> GemRepository:
    return GemRepository(session)


@router.get("/{gem_id}", response_model=GemRead)
async def get_gem(
    gem_id: int, repo: GemRepository = Depends(get_gem_repository)
) -> GemDTO:
    service = GemService(repo)
    return await service.get_gem(gem_id)


@router.get("", response_model=list[GemRead])
async def get_gems(repo: GemRepository = Depends(get_gem_repository)) -> list[GemDTO]:
    service = GemService(repo)
    gems = await service.get_all_gems()
    return gems


@router.post("", status_code=201, response_model=GemRead)
async def post_gems(
    gem_data: GemCreate,
    repo: GemRepository = Depends(get_gem_repository),
    current_user: CurrentUser = Depends(require_role("seller", "admin")),
) -> GemDTO:
    service = GemService(repo)
    return await service.create_gem(
        name=gem_data.name,
        price=gem_data.price,
        stock=gem_data.stock,
        owner_id=current_user.id,
    )


@router.put("/{gem_id}", status_code=200, response_model=GemRead)
async def put_gem(
    gem_id: int,
    gem_data: GemCreate,
    repo: GemRepository = Depends(get_gem_repository),
    current_user: CurrentUser = Depends(require_role("seller", "admin")),
) -> GemDTO:
    service = GemService(repo)

    return await service.update_gem(
        gem_id=gem_id,
        name=gem_data.name,
        price=gem_data.price,
        stock=gem_data.stock,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )


@router.delete("/{gem_id}", status_code=204)
async def delete_gem(
    gem_id: int,
    repo: GemRepository = Depends(get_gem_repository),
    current_user: CurrentUser = Depends(require_role("seller", "admin")),
) -> None:
    service = GemService(repo)
    await service.delete_gem(
        gem_id,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )
