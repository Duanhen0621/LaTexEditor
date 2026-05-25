from __future__ import annotations

from typing import Dict

# 应用层返回码（用于 `code` 字段）
SUCCESS = 0

# 常用 HTTP/业务对应的错误码（保持与历史行为兼容）
PARAM_ERROR = 400
FILE_TOO_LARGE = 413
UNSUPPORTED_FILE_TYPE = 415
INTERNAL_ERROR = 500

# 业务级别错误码（3000 系列为 AI/模型相关错误）
AI_RECOGNITION_ERROR = 3001
MODEL_NOT_LOADED = 3002
PREPROCESS_ERROR = 3003
SPEECH_RECOGNITION_ERROR = 3004
LATEX_CONVERSION_ERROR = 3005
CHAT_COMPLETION_ERROR = 3006

# 科大讯飞（非实时转写）成功码（仅用于判断成功/失败）
XFYUN_SUCCESS_CODE = "000000"

# 将返回码映射到默认 HTTP 状态码（供异常处理器使用）
DEFAULT_HTTP_STATUS: Dict[int, int] = {
    SUCCESS: 200,
    PARAM_ERROR: 400,
    FILE_TOO_LARGE: 413,
    UNSUPPORTED_FILE_TYPE: 415,
    INTERNAL_ERROR: 500,
    AI_RECOGNITION_ERROR: 500,
    MODEL_NOT_LOADED: 500,
    PREPROCESS_ERROR: 500,
    SPEECH_RECOGNITION_ERROR: 500,
    LATEX_CONVERSION_ERROR: 500,
    CHAT_COMPLETION_ERROR: 500,
}

# 框架级 HTTP 异常统一提示，不直接透传框架默认英文文案。
DEFAULT_HTTP_MESSAGE: Dict[int, str] = {
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    429: "Too Many Requests",
    413: "Payload Too Large",
    415: "Unsupported Media Type",
    422: "Unprocessable Entity",
    503: "Service Unavailable",
    500: "Internal Server Error",
}
