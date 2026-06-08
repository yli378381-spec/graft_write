"""Basic statistics: totals, per-channel, per-group, top gift."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_default_book

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=schemas.StatsOut)
def get_stats(db: Session = Depends(get_db)):
    book = get_default_book(db)
    base = select(models.GiftRecord).where(models.GiftRecord.book_id == book.id)
    gifts = list(db.execute(base).scalars().all())

    total_amount = round(sum(g.amount for g in gifts), 2)
    received = round(sum(g.amount for g in gifts if g.direction == "received"), 2)
    given = round(sum(g.amount for g in gifts if g.direction == "given"), 2)

    by_channel: dict[str, schemas.ChannelStat] = {}
    for ch in schemas.CHANNELS:
        rows = [g for g in gifts if g.channel == ch]
        by_channel[ch] = schemas.ChannelStat(
            channel=ch, total=round(sum(g.amount for g in rows), 2), count=len(rows)
        )

    by_group: dict[str, schemas.GroupStat] = {}
    for grp in schemas.RELATION_GROUPS:
        rows = [g for g in gifts if g.relation_group == grp]
        if rows:
            by_group[grp] = schemas.GroupStat(
                relation_group=grp, total=round(sum(g.amount for g in rows), 2), count=len(rows)
            )

    item_count = db.execute(
        select(func.count()).select_from(models.GiftItem).where(models.GiftItem.book_id == book.id)
    ).scalar_one()

    max_gift = None
    if gifts:
        max_gift = max(gifts, key=lambda g: g.amount)

    return schemas.StatsOut(
        total_amount=total_amount,
        total_count=len(gifts),
        item_count=item_count,
        received_amount=received,
        given_amount=given,
        by_channel=list(by_channel.values()),
        by_group=list(by_group.values()),
        max_gift=max_gift,
    )
