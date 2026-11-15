from fastapi import APIRouter, Depends, HTTPException

from auth_service.dependencies import (
    get_current_user,
    get_login_challenge_repository,
    get_otp_sender,
    get_user_repository,
)
from auth_service.dto import UserDTO
from auth_service.repositories.login_challenge_repository import (
    LoginChallengeRepository,
)
from auth_service.repositories.repositories import UserRepository
from auth_service.schemas import (
    LoginChallengeResponse,
    TokenResponse,
    UserLogin,
    UserRead,
    UserRegister,
    VerifyOTPRequest,
)
from auth_service.security.jwt import create_access_token
from auth_service.security.sms import OTPSender
from auth_service.services.auth_service import LoginChallengeService, UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201, response_model=UserRead)
async def register_user(
    user_data: UserRegister, repo: UserRepository = Depends(get_user_repository)
) -> UserDTO:
    service = UserService(repo)
    return await service.create_user(user_data.email, user_data.password)


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    return current_user


@router.post("/login", response_model=LoginChallengeResponse)
async def login(
    login_data: UserLogin,
    repo: UserRepository = Depends(get_user_repository),
    challenge_repo: LoginChallengeRepository = Depends(get_login_challenge_repository),
    sender: OTPSender = Depends(get_otp_sender),
) -> LoginChallengeResponse:
    service = UserService(repo)
    challenge_service = LoginChallengeService(challenge_repo, sender=sender)
    user = await service.authenticate_user(login_data.email, login_data.password)

    challenge = await challenge_service.create_challenge(user.id)

    return LoginChallengeResponse(
        challenge_id=challenge.id,
        message="Verification required",
    )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    challenge_data: VerifyOTPRequest,
    challenge_repo: LoginChallengeRepository = Depends(get_login_challenge_repository),
    repo: UserRepository = Depends(get_user_repository),
) -> TokenResponse:
    challenge_service = LoginChallengeService(challenge_repo)
    user_service = UserService(repo)
    user_id = await challenge_service.verify_challenge(
        challenge_data.challenge_id, challenge_data.code
    )
    user = await user_service.get_by_id(user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user)
    return TokenResponse(access_token=token)
