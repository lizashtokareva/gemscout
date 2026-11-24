from pathlib import Path

import jwt

BASE_DIR = Path(__file__).resolve().parents[3]
PUBLIC_KEY_PATH = BASE_DIR / "keys" / "public.pem"


def verify_access_token(token: str) -> dict:
    public_key = PUBLIC_KEY_PATH.read_text(encoding="utf-8")
    payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        issuer="gemscout-auth",
        audience="gemscout-api",
        options={"require": ["sub", "iat", "exp", "iss", "aud", "role"]},
    )
    role = payload["role"]
    if not isinstance(role, str) or role not in {"admin", "user", "seller"}:
        raise jwt.InvalidTokenError("Invalid role")
    return payload
