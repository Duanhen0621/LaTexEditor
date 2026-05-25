from __future__ import annotations

from fastapi import APIRouter, File, Form, Request, UploadFile

router = APIRouter(prefix="/ai", tags=["speech"])


@router.post("/speech")
async def recognize_speech(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form("cn"),
):
    service = request.app.state.speech_service
    result = await service.recognize(file=file, language=language)
    return result
