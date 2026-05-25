from __future__ import annotations

from typing import Any

from app.core import status_codes


def success_response(data: Any = None) -> dict[str, Any]:
    return {
        "code": status_codes.SUCCESS,
        "message": "success",
        "data": data or {},
    }


def error_response(code: int, message: str, detail: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code,
        "message": message,
        "data": {},
    }
    if detail is not None:
        payload["data"] = {"detail": detail}
    return payload
