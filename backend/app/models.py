"""SQLAlchemy ORM models for the basic (free) tier."""
from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import String, Integer, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _now() -> datetime:
    return datetime.utcnow()


class Book(Base):
    """A single ledger (账本). The free tier is single-account, one book per user."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), default="我的礼金账本")
    # Optional 4-6 digit lock. Stored as a salted hash, never plaintext.
    password_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    password_salt: Mapped[str | None] = mapped_column(String(32), nullable=True)
    password_hint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    gifts: Mapped[list["GiftRecord"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
    items: Mapped[list["GiftItem"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )


class GiftRecord(Base):
    """A single money gift entry (礼金记录)."""

    __tablename__ = "gift_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), index=True)

    guest_name: Mapped[str] = mapped_column(String(64), index=True)
    # relative / friend / colleague / family / other
    relation_group: Mapped[str] = mapped_column(String(16), default="other", index=True)
    relation_detail: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # cash / wechat / alipay
    channel: Mapped[str] = mapped_column(String(16), default="cash", index=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    # received (收礼) / given (随礼). Free tier defaults to received.
    direction: Mapped[str] = mapped_column(String(16), default="received", index=True)
    event_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=_now, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    book: Mapped[Book] = relationship(back_populates="gifts")


class GiftItem(Base):
    """A physical gift entry (实物礼品) - text record only in the free tier."""

    __tablename__ = "gift_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), index=True)

    guest_name: Mapped[str] = mapped_column(String(64), index=True)
    relation_group: Mapped[str] = mapped_column(String(16), default="other", index=True)
    item_name: Mapped[str] = mapped_column(String(128))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=_now, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    book: Mapped[Book] = relationship(back_populates="items")


class Reminder(Base):
    """A custom reminder node (生日/节日/喜事) with an optional blessing text."""

    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), index=True)

    title: Mapped[str] = mapped_column(String(64))
    # birthday / festival / event
    kind: Mapped[str] = mapped_column(String(16), default="event", index=True)
    remind_date: Mapped[date] = mapped_column(Date, index=True)
    blessing_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    done: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    book: Mapped[Book] = relationship(back_populates="reminders")
