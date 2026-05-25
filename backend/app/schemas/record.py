from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RecordCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    input_type: str | None = None
    raw_text: str | None = None
    record_id: int | None = None


class RecordUpdateRequest(BaseModel):
    content: str | None = None
    raw_text: str | None = None


class RecordItem(BaseModel):
    record_id: int
    title: str
    content: str
    input_type: str | None = None
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class RecordDetail(BaseModel):
    record_id: int
    title: str
    content: str
    input_type: str | None = None
    raw_text: str | None = None
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class RecordListData(BaseModel):
    total: int
    page: int
    page_size: int
    list: list[RecordItem]
