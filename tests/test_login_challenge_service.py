import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from auth_service.exceptions import (
    AttemptsError,
    CodeAlreadyUsedError,
    CodeExpiredError,
    InvalidCredentialsError,
)
from auth_service.security.otp import hash_otp
from auth_service.services.auth_service import LoginChallengeService


@pytest.mark.asyncio
async def test_verify_challenge_not_found() -> None:
    repository = AsyncMock()
    repository.get_for_update.return_value = None

    service = LoginChallengeService(repository)
    challenge_id = uuid.uuid4()
    with pytest.raises(InvalidCredentialsError):
        await service.verify_challenge(challenge_id, code="123456")

    repository.get_for_update.assert_awaited_once_with(challenge_id)


@pytest.mark.asyncio
async def test_verify_challenge_already_used() -> None:
    challenge_id = uuid.uuid4()
    code = "123456"

    repository = AsyncMock()

    challenge = SimpleNamespace(
        id=challenge_id,
        is_used=True,
    )

    repository.get_for_update.return_value = challenge

    service = LoginChallengeService(repository)

    with pytest.raises(CodeAlreadyUsedError):
        await service.verify_challenge(challenge_id, code)

    repository.mark_as_used.assert_not_awaited()
    repository.increment_attempts.assert_not_awaited()
    repository.commit.assert_not_awaited()

    repository.get_for_update.assert_awaited_once_with(challenge_id)


@pytest.mark.asyncio
async def test_verify_challenge_expired() -> None:
    challenge_id = uuid.uuid4()
    code = "123456"

    repository = AsyncMock()
    service = LoginChallengeService(repository)

    challenge = SimpleNamespace(
        id=challenge_id,
        is_used=False,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )
    repository.get_for_update.return_value = challenge
    with pytest.raises(CodeExpiredError):
        await service.verify_challenge(challenge_id, code)
    repository.get_for_update.assert_awaited_once_with(challenge_id)
    repository.mark_as_used.assert_not_awaited()


@pytest.mark.asyncio
async def test_verify_challenge_max_attempts() -> None:
    challenge_id = uuid.uuid4()
    code = "123456"
    repository = AsyncMock()
    service = LoginChallengeService(repository)
    challenge = SimpleNamespace(
        id=challenge_id,
        is_used=False,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        attempts=4,
    )
    repository.get_for_update.return_value = challenge
    with pytest.raises(AttemptsError):
        await service.verify_challenge(challenge_id, code)
    repository.mark_as_used.assert_not_awaited()
    repository.increment_attempts.assert_not_awaited()
    repository.commit.assert_not_awaited()

    repository.get_for_update.assert_awaited_once_with(challenge_id)


@pytest.mark.asyncio
async def test_verify_challenge_wrong_code() -> None:
    challenge_id = uuid.uuid4()
    correct_code = "123456"
    wrong_code = "654321"

    repository = AsyncMock()

    challenge = SimpleNamespace(
        id=challenge_id,
        user_id=uuid.uuid4(),
        code_hash=hash_otp(correct_code, challenge_id),
        is_used=False,
        attempts=0,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    repository.get_for_update.return_value = challenge
    service = LoginChallengeService(repository)

    with pytest.raises(InvalidCredentialsError):
        await service.verify_challenge(challenge_id, wrong_code)

    repository.increment_attempts.assert_awaited_once_with(challenge)
    repository.commit.assert_awaited_once()

    repository.mark_as_used.assert_not_awaited()
    repository.get_for_update.assert_awaited_once_with(challenge_id)


@pytest.mark.asyncio
async def test_verify_challenge_success() -> None:
    challenge_id = uuid.uuid4()
    user_id = uuid.uuid4()
    code = "123456"

    repository = AsyncMock()

    challenge = SimpleNamespace(
        id=challenge_id,
        user_id=user_id,
        code_hash=hash_otp(code, challenge_id),
        is_used=False,
        attempts=0,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    repository.get_for_update.return_value = challenge
    service = LoginChallengeService(repository)

    result = await service.verify_challenge(challenge_id, code)

    assert result == challenge.user_id
    repository.mark_as_used.assert_awaited_once_with(challenge)
    repository.commit.assert_awaited_once()
    repository.increment_attempts.assert_not_awaited()
