import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.repositories.repositories import UserRepository


@pytest.mark.asyncio
async def test_create_and_get_user(db_session: AsyncSession) -> None:
    # Arrange
    repository = UserRepository(db_session)
    email = f"test-{uuid.uuid4().hex}@example.com"

    # Act
    created_user = await repository.create(
        email=email,
        password_hash="test-password-hash",
    )

    await repository.commit()

    found_user = await repository.get_by_email(email)

    # Assert
    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.email == email
