import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.exceptions import InvalidCredentialsError
from auth_service.repositories.login_challenge_repository import (
    LoginChallengeRepository,
)
from auth_service.repositories.repositories import UserRepository
from auth_service.security.otp import hash_otp
from auth_service.services.auth_service import LoginChallengeService


@pytest.mark.asyncio
async def test_wrong_otp_in_database(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    challenge_repo = LoginChallengeRepository(db_session)
    challenge_service = LoginChallengeService(challenge_repo)
    user = await user_repo.create(
        email=f"test-{uuid.uuid4().hex}@example.com",
        password_hash="test-hash",
    )
    await user_repo.commit()

    challenge_id = uuid.uuid4()
    correct_code = "123456"

    await challenge_repo.create(
        challenge_id=challenge_id,
        user_id=user.id,
        code_hash=hash_otp(correct_code, challenge_id),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    await challenge_repo.commit()
    with pytest.raises(InvalidCredentialsError):
        await challenge_service.verify_challenge(
            challenge_id=challenge_id,
            code="234651",
        )

    saved_challenge = await challenge_repo.get_by_id(challenge_id)
    assert saved_challenge is not None
    assert saved_challenge.attempts == 1
    assert saved_challenge.is_used is False
