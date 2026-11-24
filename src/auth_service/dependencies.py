from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.database import get_session
from auth_service.dto import UserDTO
from auth_service.repositories.login_challenge_repository import (
    LoginChallengeRepository,
)
from auth_service.repositories.repositories import UserRepository
from auth_service.security.jwt import decode_access_token
from auth_service.security.sms import OTPSender

bearer_scheme = HTTPBearer()


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    return UserRepository(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repository),
) -> UserDTO:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = UUID(payload["sub"])
    user = await repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_login_challenge_repository(
    session: AsyncSession = Depends(get_session),
) -> LoginChallengeRepository:
    return LoginChallengeRepository(session)


def get_otp_sender() -> OTPSender:
    raise HTTPException(
        status_code=503,
        detail="SMS delivery is not configured",
    )
