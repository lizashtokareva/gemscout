from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from gem_service.database import get_session
from gem_service.repositories.repositories import GemRepository
from gem_service.schemas import GemCreate, GemRead
from gem_service.services.gem_service import GemService

router = APIRouter(prefix="/gems", tags=["Gems"])


@router.get("/{gem_id}", response_model=GemRead)
async def get_gem(gem_id: int, session: AsyncSession = Depends(get_session)) -> GemRead:
    repo = GemRepository(session)
    service = GemService(repo)
    gem = await service.get_gem(gem_id)

    return gem


@router.get("", response_model=list[GemRead])
async def get_gems(session: AsyncSession = Depends(get_session)) -> list[GemRead]:
    repo = GemRepository(session)
    service = GemService(repo)
    gems = await service.get_all_gems()
    return gems


@router.post("", status_code=201, response_model=GemRead)
async def post_gems(
    gem_data: GemCreate, session: AsyncSession = Depends(get_session)
) -> GemRead:
    repo = GemRepository(session)
    service = GemService(repo)
    gem = await service.create_gem(gem_data.name, gem_data.price, gem_data.stock)
    await session.commit()
    return gem


@router.put("/{gem_id}", status_code=200, response_model=GemRead)
async def put_gem(
    gem_id: int, gem_data: GemCreate, session: AsyncSession = Depends(get_session)
) -> GemRead:
    repo = GemRepository(session)
    service = GemService(repo)
    gem = await service.update_gem(
        gem_id, gem_data.name, gem_data.price, gem_data.stock
    )

    await session.commit()
    return gem


@router.delete("/{gem_id}", status_code=204)
async def delete_gem(gem_id: int, session: AsyncSession = Depends(get_session)) -> None:
    repo = GemRepository(session)
    service = GemService(repo)
    await service.delete_gem(gem_id)

    await session.commit()
