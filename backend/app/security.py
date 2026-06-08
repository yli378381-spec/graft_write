"""Password hashing helpers for the ledger lock (stdlib only, no extra deps)."""
from __future__ import annotations

import hashlib
import hmac
import os


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Return (hash_hex, salt_hex) using PBKDF2-HMAC-SHA256."""
    salt_bytes = bytes.fromhex(salt) if salt else os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 120_000)
    return dk.hex(), salt_bytes.hex()


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    candidate, _ = hash_password(password, salt)
    return hmac.compare_digest(candidate, password_hash)
