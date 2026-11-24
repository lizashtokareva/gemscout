import uuid
from typing import Awaitable, Callable

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from gem_service.schemas import CurrentUser
from gem_service.security import verify_access_token

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    token = credentials.credentials
    try:
        payload = verify_access_token(token)
        sub = payload["sub"]
        role = payload["role"]
        return CurrentUser(id=uuid.UUID(sub), role=role)

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(*allowed_roles: str) -> Callable[..., Awaitable[CurrentUser]]:
    async def check_role(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Permission denied",
            )

        return current_user

    return check_role
