from datetime import datetime, timedelta, timezone

import jwt

from auth_service.dto import UserDTO


def create_access_token(user: UserDTO) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "iss": "gemscout-auth",
        "aud": "gemscout-api",
        "role": user.role,
    }
    with open("keys/private.pem") as f:
        private_key = f.read()
    jwt_token = jwt.encode(payload, private_key, algorithm="RS256")
    return jwt_token


def decode_access_token(token: str) -> dict:
    with open("keys/public.pem") as f:
        public_key = f.read()
    payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        issuer="gemscout-auth",
        audience="gemscout-api",
        options={"require": ["sub", "iat", "exp", "iss", "aud"]},
    )
    return payload
