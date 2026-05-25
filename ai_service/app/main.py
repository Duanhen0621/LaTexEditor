from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.ocr import router as ocr_router
from app.api.routes.chat import router as chat_router
from app.api.routes.speech import router as speech_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.services.chat_service import ChatService
from app.services.ocr_service import OCRService
from app.services.speech_service import SpeechService


@asynccontextmanager
async def lifespan(app: FastAPI):

    settings = get_settings()

    app.state.settings = settings

    app.state.ocr_service = OCRService(
        max_upload_size=settings.max_upload_size,
        simpletex_app_id=settings.simpletex_app_id,
        simpletex_app_secret=settings.simpletex_app_secret,
        simpletex_base_url=settings.simpletex_base_url,
        simpletex_ocr_endpoint=settings.simpletex_ocr_endpoint,
    )

    app.state.speech_service = SpeechService(
        xfyun_app_id=settings.xfyun_app_id,
        xfyun_secret_key=settings.xfyun_secret_key,
        xfyun_base_url=settings.xfyun_base_url,
        xfyun_upload_endpoint=settings.xfyun_upload_endpoint,
        xfyun_result_endpoint=settings.xfyun_result_endpoint,
        xfyun_result_type=settings.xfyun_result_type,
        xfyun_upload_duration=settings.xfyun_upload_duration,
        xfyun_poll_interval_seconds=settings.xfyun_poll_interval_seconds,
        xfyun_max_poll_times=settings.xfyun_max_poll_times,
    )

    app.state.chat_service = ChatService(
        deepseek_api_key=settings.deepseek_api_key,
        deepseek_base_url=settings.deepseek_base_url,
        deepseek_model=settings.deepseek_model,
        deepseek_timeout=settings.deepseek_timeout,
        deepseek_reasoning_effort=settings.deepseek_reasoning_effort,
        deepseek_thinking_enabled=settings.deepseek_thinking_enabled,
    )

    yield


def create_app() -> FastAPI:

    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # 配置CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有源（开发环境），生产环境应该指定具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册全局异常处理器
    register_exception_handlers(app)
    # 注册路由
    app.include_router(ocr_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(speech_router, prefix="/api/v1")
    
    return app

app = create_app()
