from __future__ import annotations

# IMAGE_EXTENSIONS 是一个集合字面量。
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
# AUDIO_EXTENSIONS 也是一个集合字面量。
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg"}

# IMAGE_CONTENT_TYPES 保存允许的图片 MIME 类型集合。
IMAGE_CONTENT_TYPES = {"image/png", "image/jpeg", "image/webp"}
# AUDIO_CONTENT_TYPES 保存允许的音频 MIME 类型集合。
AUDIO_CONTENT_TYPES = {"audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3", "audio/mp4", "audio/ogg"}


def _extension(filename: str) -> str:
    # lower() 把文件名统一成小写。
    lower = filename.lower()
    # rfind(".") 返回最后一个点的位置。
    dot_index = lower.rfind(".")
    # 三元表达式：如果找到点就切片取扩展名，否则返回空串。
    return lower[dot_index:] if dot_index >= 0 else ""


def normalize_content_type(content_type: str | None) -> str:
    # split(";", maxsplit=1) 按分号切开，只保留主类型。
    return (content_type or "").split(";", maxsplit=1)[0].strip().lower()


def is_allowed_image(filename: str, content_type: str) -> bool:
    # in 是集合成员判断运算符。
    return _extension(filename) in IMAGE_EXTENSIONS or normalize_content_type(content_type) in IMAGE_CONTENT_TYPES


def is_allowed_audio(filename: str, content_type: str) -> bool:
    # 复用相同的判断逻辑，只是白名单换成音频集合。
    return _extension(filename) in AUDIO_EXTENSIONS or normalize_content_type(content_type) in AUDIO_CONTENT_TYPES


def is_allowed_file(filename: str, content_type: str, file_kind: str) -> bool:
    # if/elif/else 是条件分支语句。
    if file_kind == "image":
        return is_allowed_image(filename, content_type)
    if file_kind == "audio":
        return is_allowed_audio(filename, content_type)
    return False
 