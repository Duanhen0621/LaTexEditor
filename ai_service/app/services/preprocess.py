from __future__ import annotations

from fastapi import UploadFile

from app.core.exceptions import FileTooLargeError, ParameterError, UnsupportedFileTypeError
from app.utils.file_utils import is_allowed_audio, is_allowed_image, normalize_content_type


async def read_upload_file(upload_file: UploadFile, max_size: int) -> None:
    if upload_file.filename is None:
        raise ParameterError("file name is required")
    content = await upload_file.read()
    if not content:
        raise ParameterError("file is empty")
    if len(content) > max_size:
        raise FileTooLargeError()
    await upload_file.seek(0)

async def read_upload_file_without_size_limit(upload_file: UploadFile) -> None:
    if upload_file.filename is None:
        raise ParameterError("file name is required")
    content = await upload_file.read()
    if not content:
        raise ParameterError("file is empty")
    await upload_file.seek(0)

def validate_image_file(upload_file: UploadFile) -> None:
    # upload_file.content_type 是 MIME 类型字符串。
    content_type = normalize_content_type(upload_file.content_type)
    # or 表示扩展名或 MIME 任意一个满足即可。
    if not is_allowed_image(upload_file.filename or "", content_type):
        raise UnsupportedFileTypeError("image file type not supported")

def validate_audio_file(upload_file: UploadFile) -> None:
    # normalize_content_type(...) 用来标准化 content-type。
    content_type = normalize_content_type(upload_file.content_type)
    # is_allowed_audio(...) 判断文件是否在音频白名单内。
    if not is_allowed_audio(upload_file.filename or "", content_type):
        raise UnsupportedFileTypeError("audio file type not supported")
