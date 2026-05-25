from __future__ import annotations

from fastapi import APIRouter, File, Form, Request, UploadFile

router = APIRouter(prefix="/ai", tags=["ocr"])


@router.post("/ocr")
async def recognize_ocr(
    request: Request,
    file: UploadFile = File(...),
):
    service = request.app.state.ocr_service
    result = await service.recognize(file=file)
    return result
