from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    # 各类配置，从 .env 或环境变量中读取
    app_name: str
    app_version: str
    app_host: str
    app_port: int
    debug: bool
    max_upload_size: int
    log_level: str
    
    simpletex_app_id: str
    simpletex_app_secret: str
    simpletex_base_url: str
    simpletex_ocr_endpoint: str
    simpletex_timeout: float

    xfyun_app_id: str
    xfyun_secret_key: str
    xfyun_base_url: str
    xfyun_upload_endpoint: str
    xfyun_result_endpoint: str
    xfyun_result_type: str
    xfyun_upload_duration: int
    xfyun_poll_interval_seconds: float
    xfyun_max_poll_times: int

    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_model: str
    deepseek_timeout: float
    deepseek_reasoning_effort: str
    deepseek_thinking_enabled: bool


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    
    return Settings()
