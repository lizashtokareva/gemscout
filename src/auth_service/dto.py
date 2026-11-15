import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserDTO:
    id: uuid.UUID
    email: str
    role: str
    password_hash: str
    is_active: bool
    created_at: datetime


@dataclass(frozen=True)
class LoginChallengeDTO:
    id: uuid.UUID
    user_id: uuid.UUID
    code_hash: str
    expires_at: datetime
    attempts: int
    is_used: bool
    created_at: datetime
