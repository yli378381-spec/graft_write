"""Shared dependencies."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def get_default_book(db: Session) -> models.Book:
    """The free tier is single-account; resolve (or lazily create) the one book."""
    book = db.execute(select(models.Book).order_by(models.Book.id).limit(1)).scalar_one_or_none()
    if book is None:
        book = models.Book(name="我的礼金账本")
        db.add(book)
        db.commit()
        db.refresh(book)
    return book
