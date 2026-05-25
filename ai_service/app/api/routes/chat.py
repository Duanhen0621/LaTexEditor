from __future__ import annotations

from fastapi import APIRouter, Form, Request

router = APIRouter(prefix="/ai", tags=["chat"])


@router.post("/chat")
async def chat(
    request: Request,
    message: str = Form(..., min_length=1),
    system_prompt: str | None = Form(None),
):
    service = request.app.state.chat_service
    result = await service.chat(message=message, system_prompt=system_prompt)
    return result
