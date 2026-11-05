from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from gem_service.database import get_session
from gem_service.models import Gem
from gem_service.repositories.repositories import GemRepository
from gem_service.schemas import GemCreate, GemRead

router = APIRouter(prefix="/gems", tags=["Gems"])

@router.get("/{gem_id}")
async def get_gem(
    gem_id: int,
    session: AsyncSession = Depends(get_session)
):
    repo = GemRepository(session)
    gem = await repo.get_by_id(gem_id)# Получить камень через await
    if gem is None:
        raise HTTPException(status_code=404, detail="Gem not found")
    return {'id': gem.id, 'name': gem.name, 'price': gem.price, 'stock': gem.stock}

@router.get("")
async def get_gems(session: AsyncSession = Depends(get_session)):
    repo = GemRepository(session)
    gems = await repo.get_all()
    return gems

@router.post("", status_code=201, response_model=GemRead)
async def post_gems(gem_data: GemCreate, session: AsyncSession = Depends(get_session)):
    repo = GemRepository(session)
    gem = await repo.create(
        gem_data.name,
        gem_data.price,
        gem_data.stock
    )
    await session.commit()
    return gem

@router.put("/{gem_id}", status_code = 200, response_model=GemRead)
async def put_gem(
    gem_id: int,
    gem_data: GemCreate,
        session: AsyncSession = Depends(get_session)
):
    repo = GemRepository(session)
    gem = await repo.update(gem_id, gem_data.name, gem_data.price, gem_data.stock)
    if gem is None:
        raise HTTPException(status_code=404, detail="Gem not found")
    await session.commit()
    return gem

@router.delete("/{gem_id}", status_code=204)
async def delete_gem(
    gem_id: int, session: AsyncSession = Depends(get_session)
):
    repo = GemRepository(session)
    deleted = await repo.delete(gem_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Gem not found")
    await session.commit()