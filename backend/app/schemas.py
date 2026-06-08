"""Pydantic request/response schemas."""
from __future__ import annotations

from datetime import datetime, date

from pydantic import BaseModel, Field, ConfigDict

RELATION_GROUPS = {"relative", "friend", "colleague", "family", "other"}
CHANNELS = {"cash", "wechat", "alipay"}
DIRECTIONS = {"received", "given"}
REMINDER_KINDS = {"birthday", "festival", "event"}


# ---------- Gift records ----------
class GiftBase(BaseModel):
    guest_name: str = Field(min_length=1, max_length=64)
    relation_group: str = "other"
    relation_detail: str | None = None
    channel: str = "cash"
    amount: float = Field(ge=0)
    direction: str = "received"
    event_name: str | None = None
    note: str | None = None
    recorded_at: datetime | None = None


class GiftCreate(GiftBase):
    pass


class GiftUpdate(BaseModel):
    guest_name: str | None = Field(default=None, max_length=64)
    relation_group: str | None = None
    relation_detail: str | None = None
    channel: str | None = None
    amount: float | None = Field(default=None, ge=0)
    direction: str | None = None
    event_name: str | None = None
    note: str | None = None
    recorded_at: datetime | None = None


class GiftOut(GiftBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    recorded_at: datetime
    created_at: datetime


# ---------- Gift items (physical) ----------
class ItemBase(BaseModel):
    guest_name: str = Field(min_length=1, max_length=64)
    relation_group: str = "other"
    item_name: str = Field(min_length=1, max_length=128)
    quantity: int = Field(default=1, ge=1)
    note: str | None = None
    recorded_at: datetime | None = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    guest_name: str | None = None
    relation_group: str | None = None
    item_name: str | None = None
    quantity: int | None = Field(default=None, ge=1)
    note: str | None = None
    recorded_at: datetime | None = None


class ItemOut(ItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    recorded_at: datetime
    created_at: datetime


# ---------- Reminders ----------
class ReminderBase(BaseModel):
    title: str = Field(min_length=1, max_length=64)
    kind: str = "event"
    remind_date: date
    blessing_text: str | None = None


class ReminderCreate(ReminderBase):
    pass


class ReminderUpdate(BaseModel):
    title: str | None = None
    kind: str | None = None
    remind_date: date | None = None
    blessing_text: str | None = None
    done: int | None = None


class ReminderOut(ReminderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    done: int
    created_at: datetime


# ---------- Stats ----------
class ChannelStat(BaseModel):
    channel: str
    total: float
    count: int


class GroupStat(BaseModel):
    relation_group: str
    total: float
    count: int


class StatsOut(BaseModel):
    total_amount: float
    total_count: int
    item_count: int
    received_amount: float
    given_amount: float
    by_channel: list[ChannelStat]
    by_group: list[GroupStat]
    max_gift: GiftOut | None = None


# ---------- Lock ----------
class LockSetIn(BaseModel):
    password: str = Field(min_length=4, max_length=6, pattern=r"^\d+$")
    hint: str | None = Field(default=None, max_length=64)


class LockVerifyIn(BaseModel):
    password: str = Field(min_length=4, max_length=6)


class LockStatusOut(BaseModel):
    enabled: bool
    hint: str | None = None


class OkOut(BaseModel):
    ok: bool
    message: str | None = None


# ---------- Blessing template ----------
class BlessingTemplate(BaseModel):
    id: str
    scene: str
    relation: str
    title: str
    content: str


# ---------- Duplicate check ----------
class DuplicateOut(BaseModel):
    duplicate: bool
    matches: list[GiftOut] = []
