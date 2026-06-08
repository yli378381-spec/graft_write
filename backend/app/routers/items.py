"""Physical gift items (实物礼品) - simple text records."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_default_book

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("", response_model=list[schemas.ItemOut])
def list_items(
    db: Session = Depends(get_db),
    group: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
):
    book = get_default_book(db)
    stmt = select(models.GiftItem).where(models.GiftItem.book_id == book.id)
    if group:
        stmt = stmt.where(models.GiftItem.relation_group == group)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(
            (models.GiftItem.guest_name.like(like)) | (models.GiftItem.item_name.like(like))
        )
    stmt = stmt.order_by(models.GiftItem.recorded_at.desc())
    return list(db.execute(stmt).scalars().all())


@router.post("", response_model=schemas.ItemOut, status_code=201)
def create_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    if payload.relation_group not in schemas.RELATION_GROUPS:
        raise HTTPException(422, f"非法关系分组: {payload.relation_group}")
    book = get_default_book(db)
    item = models.GiftItem(
        book_id=book.id,
        guest_name=payload.guest_name.strip(),
        relation_group=payload.relation_group,
        item_name=payload.item_name.strip(),
        quantity=payload.quantity,
        note=payload.note,
        recorded_at=payload.recorded_at or datetime.utcnow(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=schemas.ItemOut)
def update_item(item_id: int, payload: schemas.ItemUpdate, db: Session = Depends(get_db)):
    item = db.get(models.GiftItem, item_id)
    if not item:
        raise HTTPException(404, "记录不存在")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", response_model=schemas.OkOut)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.GiftItem, item_id)
    if not item:
        raise HTTPException(404, "记录不存在")
    db.delete(item)
    db.commit()
    return schemas.OkOut(ok=True, message="已删除")
