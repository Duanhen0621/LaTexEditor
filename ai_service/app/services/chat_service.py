from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from app.core.exceptions import ChatCompletionError
from app.core.response import success_response


@dataclass(slots=True)
class DeepSeekChatResponse:
    reply: str
    model: str | None
    request_id: str | None
    usage: dict[str, Any] | None


class ChatService:
    def __init__(
        self,
        deepseek_api_key: str = "",
        deepseek_base_url: str = "https://api.deepseek.com",
        deepseek_model: str = "deepseek-v4-pro",
        deepseek_timeout: float = 10.0,
        deepseek_reasoning_effort: str = "high",
        deepseek_thinking_enabled: bool = True,
    ) -> None:
        self.deepseek_api_key = deepseek_api_key
        self.deepseek_base_url = deepseek_base_url.rstrip("/")
        self.deepseek_model = deepseek_model
        self.deepseek_timeout = deepseek_timeout
        self.deepseek_reasoning_effort = deepseek_reasoning_effort
        self.deepseek_thinking_enabled = deepseek_thinking_enabled
        self.client = OpenAI(api_key=self.deepseek_api_key, base_url=self.deepseek_base_url)

    def _build_messages(self, message: str, system_prompt: str | None) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        return messages

    def _chat_completions(
        self,
        message: str,
        system_prompt: str | None,
    ) -> DeepSeekChatResponse:
        payload_kwargs: dict[str, Any] = {
            "model": self.deepseek_model,
            "messages": self._build_messages(message=message, system_prompt=system_prompt),
            "stream": False,
            "reasoning_effort": self.deepseek_reasoning_effort,
        }
        if self.deepseek_thinking_enabled:
            payload_kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

        try:
            response = self.client.chat.completions.create(**payload_kwargs)
        except Exception as exc:  # OpenAI SDK / network / auth errors are unified here.
            raise ChatCompletionError(str(exc)) from exc

        choices = getattr(response, "choices", None) or []
        if not choices:
            raise ChatCompletionError("deepseek returned empty choices")

        first_choice = choices[0]
        message_obj = getattr(first_choice, "message", None)
        reply = getattr(message_obj, "content", None) if message_obj is not None else None
        if not reply:
            raise ChatCompletionError("deepseek returned empty content")

        usage_obj = getattr(response, "usage", None)
        usage = None
        if usage_obj is not None:
            usage = usage_obj.model_dump() if hasattr(usage_obj, "model_dump") else dict(getattr(usage_obj, "__dict__", {}))

        return DeepSeekChatResponse(
            reply=str(reply),
            model=getattr(response, "model", None) or self.deepseek_model,
            request_id=getattr(response, "id", None),
            usage=usage,
        )

    async def chat(self, message: str, system_prompt: str | None = None) -> dict[str, Any]:
        if not message or not message.strip():
            raise ChatCompletionError("message is required")
        if not self.deepseek_api_key:
            raise ChatCompletionError("deepseek client not configured")

        response = await asyncio.to_thread(self._chat_completions, message.strip(), system_prompt)
        result = {
            "reply": response.reply,
            "model": response.model,
        }
        if response.usage is not None:
            result["usage"] = response.usage

        return success_response(res=result, request_id=response.request_id)
