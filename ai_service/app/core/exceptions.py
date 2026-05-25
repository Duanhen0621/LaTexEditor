from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.response import error_response
from app.core import status_codes


class AppError(Exception):
    # AppError 是业务异常基类，所有自定义业务异常都应继承它。

    def __init__(self, code: int, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ParameterError(AppError):
    # 参数错误：请求参数缺失、非法或格式不正确时使用。
    def __init__(self, message: str = "parameter error") -> None:
        super().__init__(code=status_codes.PARAM_ERROR, message=message, status_code=status_codes.PARAM_ERROR)

class FileTooLargeError(AppError):
    # 文件过大异常：上传文件超出系统允许的大小上限时使用。
    def __init__(self, message: str = "file too large") -> None:
        super().__init__(code=status_codes.FILE_TOO_LARGE, message=message, status_code=status_codes.FILE_TOO_LARGE)

class UnsupportedFileTypeError(AppError):
    # 文件类型不支持异常：上传的文件格式不在允许范围内时使用。
    def __init__(self, message: str = "file type not supported") -> None:
        super().__init__(code=status_codes.UNSUPPORTED_FILE_TYPE, message=message, status_code=status_codes.UNSUPPORTED_FILE_TYPE)

class OcrRecognitionError(AppError):
    # OCR 识别失败异常：当图片识别（SimpleTex 等）出现任意上游错误时，统一归类为图片识别失败。 
    def __init__(self, message: str = "image recognition failed") -> None:
        super().__init__(code=status_codes.AI_RECOGNITION_ERROR, message=message, status_code=status_codes.INTERNAL_ERROR)

class SpeechRecognitionError(AppError):
    # 语音识别失败异常：ASR 调用失败或配置缺失时使用。
    def __init__(self, message: str = "speech recognition failed") -> None:
        super().__init__(code=status_codes.SPEECH_RECOGNITION_ERROR, message=message, status_code=status_codes.INTERNAL_ERROR)

class ChatCompletionError(AppError):
    # 对话失败异常：DeepSeek 调用失败或返回无效内容时使用。
    def __init__(self, message: str = "chat completion failed") -> None:
        super().__init__(code=status_codes.CHAT_COMPLETION_ERROR, message=message, status_code=status_codes.INTERNAL_ERROR)


def register_exception_handlers(app: FastAPI) -> None:

    # 业务异常：直接返回统一错误码结构。
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=error_response(code=exc.code, message=exc.message))

    # 参数校验异常：用于 FastAPI / Pydantic 生成的入参错误。
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=400, content=error_response(code=400, message="parameter error", detail=exc.errors()))

    # HTTP 层异常：如 404、405 等，统一格式化输出。
    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = exc.status_code if exc.status_code in status_codes.DEFAULT_HTTP_MESSAGE else status_codes.INTERNAL_ERROR
        message = status_codes.DEFAULT_HTTP_MESSAGE.get(exc.status_code, status_codes.DEFAULT_HTTP_MESSAGE[status_codes.INTERNAL_ERROR])
        return JSONResponse(status_code=exc.status_code, content=error_response(code=code, message=message))

    # 未预期异常：兜底，防止服务直接暴露堆栈。
    @app.exception_handler(Exception)
    async def handle_unknown_error(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status_codes.INTERNAL_ERROR, content=error_response(code=status_codes.INTERNAL_ERROR, message="internal server error"))
