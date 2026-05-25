from __future__ import annotations

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User


def get_current_user(
    request: Request,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        raise UnauthorizedError()

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise UnauthorizedError()

    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedError()

    user_id = payload.get("user_id")
    if user_id is None:
        raise UnauthorizedError()

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise UnauthorizedError()

    return user
