from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import UploadFile

from app.core import status_codes
from app.core.exceptions import SpeechRecognitionError
from app.core.response import success_response
from app.services.preprocess import read_upload_file_without_size_limit, validate_audio_file


@dataclass(slots=True)
class XFYUNUploadResponse:
    code: str | None
    desc_info: str | None
    order_id: str | None


@dataclass(slots=True)
class XFYUNResultResponse:
    code: str | None
    desc_info: str | None
    status: int | None
    order_result: str | None


class SpeechService:
    def __init__(
        self,
        xfyun_app_id: str = "",
        xfyun_secret_key: str = "",
        xfyun_base_url: str = "https://raasr.xfyun.cn/v2/api",
        xfyun_upload_endpoint: str = "/upload",
        xfyun_result_endpoint: str = "/getResult",
        xfyun_result_type: str = "transfer",
        xfyun_upload_duration: int = 200,
        xfyun_poll_interval_seconds: float = 2.0,
        xfyun_max_poll_times: int = 60,
    ) -> None:
        self.xfyun_app_id = xfyun_app_id
        self.xfyun_secret_key = xfyun_secret_key
        self.xfyun_base_url = xfyun_base_url.rstrip("/")
        self.xfyun_upload_endpoint = xfyun_upload_endpoint
        self.xfyun_result_endpoint = xfyun_result_endpoint
        self.xfyun_result_type = xfyun_result_type
        self.xfyun_upload_duration = xfyun_upload_duration
        self.xfyun_poll_interval_seconds = xfyun_poll_interval_seconds
        self.xfyun_max_poll_times = xfyun_max_poll_times

    def _timestamp(self) -> str:
        return str(int(time.time()))

    def _signa(self, ts: str) -> str:
        m2 = hashlib.md5()
        m2.update((self.xfyun_app_id + ts).encode("utf-8"))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding="utf-8")
        signa = hmac.new(self.xfyun_secret_key.encode("utf-8"), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, "utf-8")
        return signa

    def _file_size(self, upload_file: UploadFile) -> int:
        file_obj = upload_file.file
        current = file_obj.tell()
        file_obj.seek(0, 2)
        size = file_obj.tell()
        file_obj.seek(current)
        return size

    def _upload_audio(self, upload_file: UploadFile, language: str) -> XFYUNUploadResponse:

        ts = self._timestamp()
        signa = self._signa(ts)
        file_size = self._file_size(upload_file)
        file_name = upload_file.filename or "audio.wav"

        params = {
            "appId": self.xfyun_app_id,
            "signa": signa,
            "ts": ts,
            "fileSize": file_size,
            "fileName": file_name,
            "duration": self.xfyun_upload_duration,
            "language": language,
        }

        raw_data = upload_file.file.read(file_size)
        upload_file.file.seek(0)

        response = httpx.post(
            f"{self.xfyun_base_url}{self.xfyun_upload_endpoint}?{urlencode(params)}",
            headers={"Content-type": "application/json"},
            data=raw_data,
        )

        payload = response.json()
        content = payload.get("content") or {}
        return XFYUNUploadResponse(
            code=payload.get("code"),
            desc_info=payload.get("descInfo"),
            order_id=content.get("orderId"),
        )

    def _get_result(self, order_id: str) -> XFYUNResultResponse:
        ts = self._timestamp()
        signa = self._signa(ts)
        params = {
            "appId": self.xfyun_app_id,
            "signa": signa,
            "ts": ts,
            "orderId": order_id,
            "resultType": self.xfyun_result_type,
        }

        response = httpx.post(
            f"{self.xfyun_base_url}{self.xfyun_result_endpoint}?{urlencode(params)}",
            headers={"Content-type": "application/json"},
        )
        payload = response.json()
        content = payload.get("content") or {}
        order_info = content.get("orderInfo") or {}

        return XFYUNResultResponse(
            code=payload.get("code"),
            desc_info=payload.get("descInfo"),
            status=order_info.get("status"),
            order_result=content.get("orderResult"),
        )

    def _extract_text(self, order_result: str | None) -> str:
        # 将讯飞返回的嵌套 JSON 结果提取成连续文本。
        if not order_result:
            return ""
        try:
            parsed = json.loads(order_result)
        except json.JSONDecodeError:
            return ""

        words: list[str] = []
        lattice = parsed.get("lattice") or []
        for segment in lattice:
            onebest = segment.get("json_1best")
            if not onebest:
                continue
            try:
                best = json.loads(onebest)
            except json.JSONDecodeError:
                continue
            st = best.get("st") or {}
            for rt in st.get("rt") or []:
                for ws in rt.get("ws") or []:
                    cw = ws.get("cw") or []
                    if cw and isinstance(cw[0], dict):
                        w = cw[0].get("w", "")
                        if w:
                            words.append(str(w))
        return "".join(words).strip()

    async def recognize(self, file: UploadFile, language: str = "cn") -> dict[str, Any]:
        
        # 各类校验
        validate_audio_file(file)
        await read_upload_file_without_size_limit(file)
        if not self.xfyun_app_id or not self.xfyun_secret_key:
            raise SpeechRecognitionError("xfyun client not configured")

        # 获取初步识别结果
        upload_result = self._upload_audio(file, language)

        # 检查识别是否成功
        upload_code = upload_result.code
        if upload_code != status_codes.XFYUN_SUCCESS_CODE:
            message = upload_result.desc_info or "speech recognition failed"
            raise SpeechRecognitionError(message)
        if not upload_result.order_id:
            raise SpeechRecognitionError("xfyun upload did not return order id")

        final_result: XFYUNResultResponse | None = None
        for _ in range(self.xfyun_max_poll_times):
            current = self._get_result(upload_result.order_id)
            if current.code != status_codes.XFYUN_SUCCESS_CODE:
                # 查询阶段如果返回非成功码，也按上游错误统一归类为语音识别失败
                message = current.desc_info or "speech recognition failed"
                raise SpeechRecognitionError(message)

            if current.status in {4, -1}:
                # 4 表示转写完成，-1 表示任务失败。
                final_result = current
                break
            # 任务仍在处理中时，按固定间隔继续轮询。
            time.sleep(self.xfyun_poll_interval_seconds)

        if final_result is None:
            raise SpeechRecognitionError("xfyun polling timed out")
        if final_result.status == -1:
            raise SpeechRecognitionError("xfyun transcription failed")

        text = self._extract_text(final_result.order_result)
        result = {
            "text": text,
            "language": language,
        }

        return success_response(res=result, request_id=upload_result.order_id)
