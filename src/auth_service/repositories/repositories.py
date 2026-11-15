import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.dto import UserDTO
from auth_service.models import User


def to_dto(user: User) -> UserDTO:
    return UserDTO(
        id=user.id,
        email=user.email,
        password_hash=user.password_hash,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def get_by_email(self, email: str) -> UserDTO | None:
        user = await self.session.scalar(select(User).where(User.email == email))
        if user is None:
            return None

        return to_dto(user)

    async def create(self, email: str, password_hash: str) -> UserDTO:
        user = User(email=email, password_hash=password_hash)

        self.session.add(user)
        await self.session.flush()

        return to_dto(user)

    async def get_by_id(self, user_id: uuid.UUID) -> UserDTO | None:
        user = await self.session.get(User, user_id)
        if user is None:
            return None
        return to_dto(user)
