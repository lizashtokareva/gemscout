import uuid
from datetime import datetime, timedelta, timezone

from auth_service.dto import LoginChallengeDTO, UserDTO
from auth_service.exceptions import (
    AttemptsError,
    CodeAlreadyUsedError,
    CodeExpiredError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from auth_service.repositories.login_challenge_repository import (
    LoginChallengeRepository,
)
from auth_service.repositories.repositories import UserRepository
from auth_service.security.otp import generate_otp, hash_otp, verify_otp
from auth_service.security.security import password_hasher
from auth_service.security.sms import OTPSender


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def create_user(self, email: str, password: str) -> UserDTO:
        exists = await self.repository.get_by_email(email)

        if exists is not None:
            raise UserAlreadyExistsError("User already exists")

        password_hash = password_hasher.hash(password)
        user = await self.repository.create(email, password_hash)
        await self.repository.commit()
        return user

    async def authenticate_user(self, email: str, password: str) -> UserDTO:
        user = await self.repository.get_by_email(email)
        if user is None:
            raise InvalidCredentialsError("Invalid credentials")

        is_valid = password_hasher.verify(password, user.password_hash)
        if not is_valid or not user.is_active:
            raise InvalidCredentialsError("Invalid credentials")

    async def get_by_id(self, user_id: uuid.UUID) -> UserDTO:
        return await self.repository.get_by_id(user_id)


class LoginChallengeService:
    def __init__(
        self,
        repository: LoginChallengeRepository,
        sender: OTPSender | None = None,
    ) -> None:
        self.repository = repository
        self.sender = sender

    async def create_challenge(self, user_id: uuid.UUID) -> LoginChallengeDTO:
        challenge_id = uuid.uuid4()
        code = generate_otp()
        code_hash = hash_otp(code, challenge_id)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        login_challenge = await self.repository.create(
            challenge_id=challenge_id,
            user_id=user_id,
            code_hash=code_hash,
            expires_at=expires_at,
        )
        await self.repository.commit()
        await self.sender.send_code(user_id, code)
        return login_challenge

    async def verify_challenge(
        self,
        challenge_id: uuid.UUID,
        code: str,
    ) -> uuid.UUID:
        challenge = await self.repository.get_for_update(challenge_id)

        if challenge is None:
            raise InvalidCredentialsError("Invalid credentials")

        if challenge.is_used:
            raise CodeAlreadyUsedError("Incorrect code")

        if datetime.now(timezone.utc) >= challenge.expires_at:
            raise CodeExpiredError("Incorrect code")

        if challenge.attempts >= 4:
            raise AttemptsError("Too many attempts. Try again later")

        if not verify_otp(code, challenge_id, challenge.code_hash):
            await self.repository.increment_attempts(challenge)
            await self.repository.commit()
            raise InvalidCredentialsError("Invalid credentials")

        await self.repository.mark_as_used(challenge)
        await self.repository.commit()
        return challenge.user_id
