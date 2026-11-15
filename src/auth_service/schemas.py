import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field

model_config = ConfigDict(from_attributes=True)


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserRead(BaseModel):
    email: EmailStr
    role: str
    id: uuid.UUID


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class LoginChallengeResponse(BaseModel):
    challenge_id: uuid.UUID
    message: str


class VerifyOTPRequest(BaseModel):
    challenge_id: uuid.UUID
    code: str = Field(pattern=r"^\d{6}$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
