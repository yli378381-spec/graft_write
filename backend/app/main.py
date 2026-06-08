"""FastAPI entrypoint for 喜鹊礼簿 (Magpie Gift Ledger) - basic tier API."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import gifts, items, reminders, stats, lock, blessings

app = FastAPI(
    title="喜鹊礼簿 API",
    description="婚礼礼金记账小程序 - 基础版(免费)后端接口",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/", tags=["meta"])
def root():
    return {"app": "喜鹊礼簿", "tier": "basic", "status": "ok"}


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok"}


app.include_router(gifts.router)
app.include_router(items.router)
app.include_router(reminders.router)
app.include_router(stats.router)
app.include_router(lock.router)
app.include_router(blessings.router)
