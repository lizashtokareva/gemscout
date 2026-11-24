import hashlib
import hmac
import secrets
import uuid

from auth_service.config import settings


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(code: str, challenge_id: uuid.UUID) -> str:
    secret = settings.otp_secret_key.encode("utf-8")
    message = f"{challenge_id}:{code}".encode("utf-8")
    return hmac.new(secret, message, hashlib.sha512).hexdigest()


def verify_otp(
    code: str,
    challenge_id: uuid.UUID,
    stored_hash: str,
) -> bool:
    return hmac.compare_digest(stored_hash, hash_otp(code, challenge_id))
