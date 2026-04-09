"""Encrypt and decrypt sensitive environment variable values."""

from __future__ import annotations

import base64
import hashlib
import hmac
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SENSITIVE_PATTERNS = ("secret", "password", "passwd", "token", "key", "api", "auth", "private")


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(p in lower for p in _SENSITIVE_PATTERNS)


def _derive_key(passphrase: str) -> bytes:
    """Derive a 32-byte key from a passphrase using SHA-256."""
    return hashlib.sha256(passphrase.encode()).digest()


def _xor_encrypt(data: bytes, key: bytes) -> bytes:
    """Simple XOR cipher (repeating key). Not production-grade; for demo purposes."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


@dataclass
class EncryptReport:
    encrypted_env: Dict[str, str]
    encrypted_keys: List[str] = field(default_factory=list)
    passphrase_hint: Optional[str] = None

    @property
    def encrypt_count(self) -> int:
        return len(self.encrypted_keys)

    def summary(self) -> str:
        return (
            f"{self.encrypt_count} key(s) encrypted: {', '.join(sorted(self.encrypted_keys))}"
            if self.encrypted_keys
            else "No keys were encrypted."
        )


def encrypt_env(
    env: Dict[str, str],
    passphrase: str,
    *,
    sensitive_only: bool = True,
    passphrase_hint: Optional[str] = None,
) -> EncryptReport:
    """Encrypt env values. If sensitive_only=True, only encrypt sensitive keys."""
    key = _derive_key(passphrase)
    result: Dict[str, str] = {}
    encrypted_keys: List[str] = []

    for k, v in env.items():
        if sensitive_only and not _is_sensitive(k):
            result[k] = v
        else:
            cipher = _xor_encrypt(v.encode(), key)
            result[k] = "ENC:" + base64.b64encode(cipher).decode()
            encrypted_keys.append(k)

    return EncryptReport(
        encrypted_env=result,
        encrypted_keys=encrypted_keys,
        passphrase_hint=passphrase_hint,
    )


def decrypt_env(env: Dict[str, str], passphrase: str) -> Dict[str, str]:
    """Decrypt all ENC:-prefixed values in the env dict."""
    key = _derive_key(passphrase)
    result: Dict[str, str] = {}

    for k, v in env.items():
        if v.startswith("ENC:"):
            raw = base64.b64decode(v[4:])
            result[k] = _xor_encrypt(raw, key).decode()
        else:
            result[k] = v

    return result
