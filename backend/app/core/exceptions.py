from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.response import error_response
from app.core import status_codes


class AppError(Exception):
    """业务异常基类"""

    def __init__(self, code: int, message: str, status_code: int | None = None) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code or status_codes.CODE_TO_HTTP.get(code, 400)
        super().__init__(message)


class WrongCredentialsError(AppError):
    def __init__(self, message: str = "用户名或密码错误") -> None:
        super().__init__(code=status_codes.WRONG_CREDENTIALS, message=message)


class UserAlreadyExistsError(AppError):
    def __init__(self, message: str = "用户已存在") -> None:
        super().__init__(code=status_codes.USER_ALREADY_EXISTS, message=message)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "未登录或 token 无效") -> None:
        super().__init__(code=status_codes.UNAUTHORIZED, message=message, status_code=401)


class NotFoundError(AppError):
    def __init__(self, message: str = "资源不存在") -> None:
        super().__init__(code=status_codes.NOT_FOUND, message=message, status_code=404)


class RateLimitError(AppError):
    def __init__(self, message: str = "登录尝试过于频繁，请 60 秒后再试") -> None:
        super().__init__(code=status_codes.RATE_LIMITED, message=message, status_code=429)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(code=exc.code, message=exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=error_response(code=400, message="请求参数错误", detail=exc.errors()),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(code=exc.status_code, message=str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def handle_unknown_error(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=error_response(code=status_codes.INTERNAL_ERROR, message="服务器内部错误"),
        )
