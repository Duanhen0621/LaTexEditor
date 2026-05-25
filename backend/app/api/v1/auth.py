from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import UserAlreadyExistsError, WrongCredentialsError
from app.core.rate_limiter import check_login_rate_limit, clear_login_rate_limit
from app.core.redis_client import get_redis
from app.core.response import success_response
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import LoginRequest, LoginResponse, RegisterRequest, UserInfo
from redis.asyncio import Redis

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise UserAlreadyExistsError()

    user = User(
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return success_response(data={
        "user_id": user.id,
        "username": user.username,
    })


@router.post("/login")
async def login(
    body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    # 获取客户端 IP
    client_ip = request.client.host if request.client else "unknown"

    # 检查登录频率限制（递增计数器）
    await check_login_rate_limit(redis, client_ip)

    user = db.query(User).filter(User.username == body.username).first()
    if not user:
        raise WrongCredentialsError()

    if not verify_password(body.password, user.hashed_password):
        raise WrongCredentialsError()

    # 登录成功，清除限流计数
    await clear_login_rate_limit(redis, client_ip)

    token = create_access_token(payload={"user_id": user.id, "username": user.username})
    return success_response(data=LoginResponse(
        token=token,
        user=UserInfo(
            user_id=user.id,
            username=user.username,
            email=user.email,
            created_at=str(user.created_at),
        ),
    ).model_dump())


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return success_response(data=UserInfo(
        user_id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=str(current_user.created_at),
    ).model_dump())
