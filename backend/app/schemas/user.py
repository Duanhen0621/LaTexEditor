from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)
    email: str | None = None


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserInfo(BaseModel):
    user_id: int
    username: str
    email: str | None = None
    created_at: str | None = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    token: str
    user: UserInfo
