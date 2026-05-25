from __future__ import annotations

import datetime
import hashlib
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Any

import httpx
from fastapi import UploadFile

from app.core.exceptions import OcrRecognitionError, FileTooLargeError
from app.services.preprocess import validate_image_file, read_upload_file
from app.core.response import success_response

def _random_str(length: int = 16) -> str:
    generated = ""
    chars = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789"
    chars_last_index = len(chars) - 1
    random_instance = Random()
    for _ in range(length):
        generated += chars[random_instance.randint(0, chars_last_index)]
    return generated

def build_simpletex_sign(app_id: str, app_secret: str) -> dict[str, str]:

    header: dict[str, str] = {}
    header["timestamp"] = str(int(datetime.datetime.now().timestamp()))
    header["random-str"] = _random_str(16)
    header["app-id"] = app_id

    pre_sign_string = ""
    sorted_keys = list(header)
    sorted_keys.sort()

    for key in sorted_keys:
        if pre_sign_string:
            pre_sign_string += "&"
        pre_sign_string += key + "=" + str(header[key])

    pre_sign_string += "&secret=" + app_secret
    header["sign"] = hashlib.md5(pre_sign_string.encode()).hexdigest()
    return header


@dataclass(slots=True)
class SimpleTexOCRResponse:
    status: bool
    http_status_code: int | None
    message: str | None
    res: dict[str, Any]
    request_id: str | None

class OCRService:
    def __init__(
        self,
        max_upload_size: int,
        simpletex_app_id: str = "",
        simpletex_app_secret: str = "",
        simpletex_base_url: str = "https://server.simpletex.cn",
        simpletex_ocr_endpoint: str = "",
    ) -> None:
        self.max_upload_size = max_upload_size
        self.simpletex_app_id = simpletex_app_id
        self.simpletex_app_secret = simpletex_app_secret
        self.simpletex_base_url = simpletex_base_url.rstrip("/")
        self.simpletex_ocr_endpoint = simpletex_ocr_endpoint

    def _build_headers(self) -> dict[str, str]:
        # 构建 SimpleTex 鉴权 header
        return build_simpletex_sign(
            app_id=self.simpletex_app_id,
            app_secret=self.simpletex_app_secret,
        )

    def _ocr_image_bytes(
        self,
        image_file: Any,
        endpoint: str,
    ) -> SimpleTexOCRResponse:
        headers = self._build_headers()
        files = {"file": image_file}
        
        response = httpx.post(
            f"{self.simpletex_base_url}{endpoint}",
            files=files,
            headers=headers,
        )

        response_json = response.json()
        response_status_code = getattr(response, "status_code", None)
        print(response_json)
        return SimpleTexOCRResponse(
            status=bool(response_json.get("status")),
            http_status_code=response_status_code if isinstance(response_status_code, int) else None,
            message=response_json.get("message"),
            res=dict(response_json.get("res") or {}),
            request_id=response_json.get("request_id"),
        )

    def _ocr_image(self, image_path: str | Path, endpoint: str, data: dict[str, Any] | None = None) -> SimpleTexOCRResponse:
        with Path(image_path).open("rb") as image_file:
            return self._ocr_image_bytes(
                image_file=image_file,
                filename=Path(image_path).name,
                endpoint=endpoint,
            )

    async def recognize(self, file: UploadFile) -> dict:
        
        # 各类校验
        validate_image_file(file)
        await read_upload_file(file, self.max_upload_size)
        if not self.simpletex_app_id or not self.simpletex_app_secret:
            raise OcrRecognitionError("simpletex client not configured")
        if not self.simpletex_ocr_endpoint:
            raise OcrRecognitionError("simpletex endpoint not configured")

        # 调用 SimpleTex 接口，直接获取结果；异常交给全局异常处理器统一处理
        response = self._ocr_image_bytes(
            image_file=file.file,
            endpoint=self.simpletex_ocr_endpoint,
        )

        # 检查识别是否成功
        if (response.http_status_code is not None and response.http_status_code != 200) or not response.status:
            # 将所有 SimpleTex 上游错误统一归类为图片识别失败，保留上游提示作为 message
            error_message = response.message or "image recognition failed"
            raise OcrRecognitionError(error_message)

        return success_response(
            res=dict(response.res or {}),
            request_id=response.request_id,
        )
