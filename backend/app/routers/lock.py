"""Ledger password lock (账本密码锁) - protects gift data on a shared device."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.deps import get_default_book
from app.security import hash_password, verify_password

router = APIRouter(prefix="/api/lock", tags=["lock"])


@router.get("/status", response_model=schemas.LockStatusOut)
def lock_status(db: Session = Depends(get_db)):
    book = get_default_book(db)
    return schemas.LockStatusOut(enabled=bool(book.password_hash), hint=book.password_hint)


@router.post("/set", response_model=schemas.OkOut)
def set_lock(payload: schemas.LockSetIn, db: Session = Depends(get_db)):
    book = get_default_book(db)
    pw_hash, salt = hash_password(payload.password)
    book.password_hash = pw_hash
    book.password_salt = salt
    book.password_hint = payload.hint
    db.commit()
    return schemas.OkOut(ok=True, message="密码已设置")


@router.post("/verify", response_model=schemas.OkOut)
def verify_lock(payload: schemas.LockVerifyIn, db: Session = Depends(get_db)):
    book = get_default_book(db)
    if not book.password_hash or not book.password_salt:
        return schemas.OkOut(ok=True, message="未设置密码")
    if verify_password(payload.password, book.password_hash, book.password_salt):
        return schemas.OkOut(ok=True, message="验证成功")
    raise HTTPException(401, "密码错误")


@router.post("/disable", response_model=schemas.OkOut)
def disable_lock(payload: schemas.LockVerifyIn, db: Session = Depends(get_db)):
    book = get_default_book(db)
    if book.password_hash and book.password_salt:
        if not verify_password(payload.password, book.password_hash, book.password_salt):
            raise HTTPException(401, "密码错误")
    book.password_hash = None
    book.password_salt = None
    book.password_hint = None
    db.commit()
    return schemas.OkOut(ok=True, message="已关闭密码锁")
