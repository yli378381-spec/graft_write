"""Money gift records: CRUD, filtering, duplicate check (防重复)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_default_book

router = APIRouter(prefix="/api/gifts", tags=["gifts"])


def _validate(channel: str | None, group: str | None, direction: str | None) -> None:
    if channel is not None and channel not in schemas.CHANNELS:
        raise HTTPException(422, f"非法支付渠道: {channel}")
    if group is not None and group not in schemas.RELATION_GROUPS:
        raise HTTPException(422, f"非法关系分组: {group}")
    if direction is not None and direction not in schemas.DIRECTIONS:
        raise HTTPException(422, f"非法收支方向: {direction}")


@router.get("", response_model=list[schemas.GiftOut])
def list_gifts(
    db: Session = Depends(get_db),
    group: str | None = Query(default=None),
    channel: str | None = Query(default=None),
    direction: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    order: str = Query(default="recorded_desc"),
):
    book = get_default_book(db)
    stmt = select(models.GiftRecord).where(models.GiftRecord.book_id == book.id)
    if group:
        stmt = stmt.where(models.GiftRecord.relation_group == group)
    if channel:
        stmt = stmt.where(models.GiftRecord.channel == channel)
    if direction:
        stmt = stmt.where(models.GiftRecord.direction == direction)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(models.GiftRecord.guest_name.like(like))

    if order == "amount_desc":
        stmt = stmt.order_by(models.GiftRecord.amount.desc())
    elif order == "amount_asc":
        stmt = stmt.order_by(models.GiftRecord.amount.asc())
    elif order == "recorded_asc":
        stmt = stmt.order_by(models.GiftRecord.recorded_at.asc())
    else:
        stmt = stmt.order_by(models.GiftRecord.recorded_at.desc())

    return list(db.execute(stmt).scalars().all())


@router.get("/check-duplicate", response_model=schemas.DuplicateOut)
def check_duplicate(
    guest_name: str = Query(min_length=1),
    direction: str = Query(default="received"),
    db: Session = Depends(get_db),
):
    """防重复录入提醒: warn if the same guest already has an entry in this direction."""
    book = get_default_book(db)
    stmt = (
        select(models.GiftRecord)
        .where(models.GiftRecord.book_id == book.id)
        .where(models.GiftRecord.guest_name == guest_name.strip())
        .where(models.GiftRecord.direction == direction)
        .order_by(models.GiftRecord.recorded_at.desc())
    )
    matches = list(db.execute(stmt).scalars().all())
    return schemas.DuplicateOut(duplicate=len(matches) > 0, matches=matches)


@router.post("", response_model=schemas.GiftOut, status_code=201)
def create_gift(payload: schemas.GiftCreate, db: Session = Depends(get_db)):
    _validate(payload.channel, payload.relation_group, payload.direction)
    book = get_default_book(db)
    gift = models.GiftRecord(
        book_id=book.id,
        guest_name=payload.guest_name.strip(),
        relation_group=payload.relation_group,
        relation_detail=payload.relation_detail,
        channel=payload.channel,
        amount=round(payload.amount, 2),
        direction=payload.direction,
        event_name=payload.event_name,
        note=payload.note,
        recorded_at=payload.recorded_at or datetime.utcnow(),
    )
    db.add(gift)
    db.commit()
    db.refresh(gift)
    return gift


@router.get("/{gift_id}", response_model=schemas.GiftOut)
def get_gift(gift_id: int, db: Session = Depends(get_db)):
    gift = db.get(models.GiftRecord, gift_id)
    if not gift:
        raise HTTPException(404, "记录不存在")
    return gift


@router.put("/{gift_id}", response_model=schemas.GiftOut)
def update_gift(gift_id: int, payload: schemas.GiftUpdate, db: Session = Depends(get_db)):
    gift = db.get(models.GiftRecord, gift_id)
    if not gift:
        raise HTTPException(404, "记录不存在")
    _validate(payload.channel, payload.relation_group, payload.direction)
    data = payload.model_dump(exclude_unset=True)
    if "guest_name" in data and data["guest_name"]:
        data["guest_name"] = data["guest_name"].strip()
    if "amount" in data and data["amount"] is not None:
        data["amount"] = round(data["amount"], 2)
    for key, value in data.items():
        setattr(gift, key, value)
    db.commit()
    db.refresh(gift)
    return gift


@router.delete("/{gift_id}", response_model=schemas.OkOut)
def delete_gift(gift_id: int, db: Session = Depends(get_db)):
    gift = db.get(models.GiftRecord, gift_id)
    if not gift:
        raise HTTPException(404, "记录不存在")
    db.delete(gift)
    db.commit()
    return schemas.OkOut(ok=True, message="已删除")
