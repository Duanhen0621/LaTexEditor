from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.response import success_response
from app.models.record import Record
from app.models.user import User
from app.schemas.record import (
    RecordCreateRequest,
    RecordDetail,
    RecordItem,
    RecordListData,
    RecordUpdateRequest,
)

router = APIRouter(prefix="/records", tags=["records"])


def _build_title(content: str) -> str:
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped:
            return stripped.replace("#", "").strip()[:50]
    return "未命名"


def _format_dt(dt) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""


@router.get("")
def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Record).filter(Record.user_id == current_user.id)

    if keyword:
        like = f"%{keyword}%"
        q = q.filter((Record.title.like(like)) | (Record.content.like(like)))

    total = q.count()
    records = q.order_by(desc(Record.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    items = [
        RecordItem(
            record_id=r.id,
            title=r.title,
            content=r.content,
            input_type=r.input_type,
            status=r.status,
            created_at=_format_dt(r.created_at),
            updated_at=_format_dt(r.updated_at),
        )
        for r in records
    ]

    return success_response(data=RecordListData(
        total=total,
        page=page,
        page_size=page_size,
        list=items,
    ).model_dump())


@router.get("/{record_id}")
def get_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id,
    ).first()
    if not record:
        raise NotFoundError("记录不存在")

    return success_response(data=RecordDetail(
        record_id=record.id,
        title=record.title,
        content=record.content,
        input_type=record.input_type,
        raw_text=record.raw_text,
        status=record.status,
        created_at=_format_dt(record.created_at),
        updated_at=_format_dt(record.updated_at),
    ).model_dump())


@router.post("")
def create_record(
    body: RecordCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.record_id is not None:
        record = db.query(Record).filter(
            Record.id == body.record_id,
            Record.user_id == current_user.id,
        ).first()
        if not record:
            raise NotFoundError("记录不存在")

        record.content = body.content
        record.title = _build_title(body.content)
        if body.input_type is not None:
            record.input_type = body.input_type
        if body.raw_text is not None:
            record.raw_text = body.raw_text

        db.commit()
        return success_response(data={"record_id": record.id})

    record = Record(
        user_id=current_user.id,
        title=_build_title(body.content),
        content=body.content,
        input_type=body.input_type,
        raw_text=body.raw_text,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return success_response(data={"record_id": record.id})


@router.put("/{record_id}")
def update_record(
    record_id: int,
    body: RecordUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id,
    ).first()
    if not record:
        raise NotFoundError("记录不存在")

    if body.content is not None:
        record.content = body.content
        record.title = _build_title(body.content)
    if body.raw_text is not None:
        record.raw_text = body.raw_text

    db.commit()

    return success_response(data={"record_id": record.id})


@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id,
    ).first()
    if not record:
        raise NotFoundError("记录不存在")

    db.delete(record)
    db.commit()

    return success_response(data={})
