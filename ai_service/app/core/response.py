from __future__ import annotations

from typing import Any

from app.core import status_codes


def success_response(res, request_id) -> dict[str, Any]:
    return {
        "code": status_codes.SUCCESS,
        "message": "success",
        "res": res,
        "request_id": request_id
    }


def error_response(code: int, message: str, detail: Any | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code,
        "message": message,
        "res": {},
        "request_id": "",
    }
    if detail is not None:
        # 当存在 detail 时，把它放在 res.detail 下以保留额外信息。
        payload["res"] = {"detail": detail}
    return payload
