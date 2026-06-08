"""Reminder nodes (生日/节日/喜事) with blessing text."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_default_book

router = APIRouter(prefix="/api/reminders", tags=["reminders"])


@router.get("", response_model=list[schemas.ReminderOut])
def list_reminders(
    db: Session = Depends(get_db),
    kind: str | None = Query(default=None),
):
    book = get_default_book(db)
    stmt = select(models.Reminder).where(models.Reminder.book_id == book.id)
    if kind:
        stmt = stmt.where(models.Reminder.kind == kind)
    stmt = stmt.order_by(models.Reminder.remind_date.asc())
    return list(db.execute(stmt).scalars().all())


@router.post("", response_model=schemas.ReminderOut, status_code=201)
def create_reminder(payload: schemas.ReminderCreate, db: Session = Depends(get_db)):
    if payload.kind not in schemas.REMINDER_KINDS:
        raise HTTPException(422, f"非法提醒类型: {payload.kind}")
    book = get_default_book(db)
    reminder = models.Reminder(
        book_id=book.id,
        title=payload.title.strip(),
        kind=payload.kind,
        remind_date=payload.remind_date,
        blessing_text=payload.blessing_text,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.put("/{reminder_id}", response_model=schemas.ReminderOut)
def update_reminder(reminder_id: int, payload: schemas.ReminderUpdate, db: Session = Depends(get_db)):
    reminder = db.get(models.Reminder, reminder_id)
    if not reminder:
        raise HTTPException(404, "提醒不存在")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(reminder, key, value)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", response_model=schemas.OkOut)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.get(models.Reminder, reminder_id)
    if not reminder:
        raise HTTPException(404, "提醒不存在")
    db.delete(reminder)
    db.commit()
    return schemas.OkOut(ok=True, message="已删除")
