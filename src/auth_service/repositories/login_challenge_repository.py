import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.dto import LoginChallengeDTO
from auth_service.models import LoginChallenge
from auth_service.repositories.repositories import to_dto


class LoginChallengeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def create(
        self,
        challenge_id: uuid.UUID,
        user_id: uuid.UUID,
        code_hash: str,
        expires_at: datetime,
    ) -> LoginChallengeDTO:
        login_challenge = LoginChallenge(
            user_id=user_id, code_hash=code_hash, expires_at=expires_at
        )
        self.session.add(login_challenge)
        await self.session.flush()
        return to_dto(login_challenge)

    async def get_by_id(
        self,
        challenge_id: uuid.UUID,
    ) -> LoginChallengeDTO | None:
        login_challenge = await self.session.get(LoginChallenge, challenge_id)
        if login_challenge is None:
            return None
        return to_dto(login_challenge)

    async def get_for_update(
        self,
        challenge_id: uuid.UUID,
    ) -> LoginChallenge | None:
        return await self.session.scalar(
            select(LoginChallenge)
            .where(LoginChallenge.id == challenge_id)
            .with_for_update()
        )

    async def increment_attempts(
        self,
        challenge: LoginChallenge,
    ) -> None:
        challenge.attempts += 1
        await self.session.flush()

    async def mark_as_used(
        self,
        challenge: LoginChallenge,
    ) -> None:
        challenge.is_used = True
        await self.session.flush()
