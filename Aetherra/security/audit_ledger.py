"""Tamper-evident append-only JSONL audit ledger."""

from __future__ import annotations

# Standard library imports
import contextlib
import hashlib
import hmac
import json
import os
import secrets
import threading
from collections import OrderedDict
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Any

AUDIT_VERSION = 1
GENESIS_HASH = "0" * 64


class AuditLedgerError(RuntimeError):
    """Base error for audit-ledger operations."""


class AuditIntegrityError(AuditLedgerError):
    """Raised when an existing ledger fails integrity validation."""


_LOCKS_GUARD = threading.Lock()
_LOCKS: dict[Path, threading.RLock] = {}


@dataclass(frozen=True, slots=True)
class _VerifiedPrefix:
    size: int
    digest: bytes
    key_digest: bytes
    line_count: int
    sequence: int
    tail_hash: str
    expires_at: float


_PREFIX_LIMIT = 64
_PREFIX_LIFETIME = 600.0
_PREFIXES: OrderedDict[Path, _VerifiedPrefix] = OrderedDict()


def _path_lock(path: Path) -> threading.RLock:
    resolved = path.resolve()
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(resolved, threading.RLock())


def _canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        default=str,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _record_hash(record: Mapping[str, Any]) -> str:
    body = {
        key: value for key, value in record.items() if key not in {"hash", "signature"}
    }
    return hashlib.sha256(_canonical(body)).hexdigest()


def _signature(secret: bytes, record_hash: str) -> str:
    return hmac.new(secret, record_hash.encode("ascii"), hashlib.sha256).hexdigest()


class SecurityAuditLedger:
    """Append and verify signed, hash-chained security audit records."""

    def __init__(self, path: Path | str, *, key_path: Path | str | None = None):
        self.path = Path(path).expanduser().resolve()
        self.key_path = (
            Path(key_path).expanduser().resolve()
            if key_path is not None
            else self.path.with_suffix(self.path.suffix + ".key")
        )
        self._lock = _path_lock(self.path)

    def append(
        self,
        *,
        actor: str,
        event_type: str,
        reason: str | None = None,
        details: Mapping[str, Any] | None = None,
        extra: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Validate the current chain, append one record, and return it."""
        if not isinstance(actor, str) or not actor.strip():
            raise ValueError("audit actor must be a non-empty string")
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("audit event_type must be a non-empty string")

        with self._lock:
            secret = self._load_or_create_secret()
            sequence, previous_hash, prefix = self._verified_tail(
                secret, for_append=True
            )
            record: dict[str, Any] = {
                "audit_version": AUDIT_VERSION,
                "sequence": sequence + 1,
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "actor": actor.strip(),
                "event_type": event_type.strip(),
                "reason": reason,
                "details": dict(details or {}),
                "prev_hash": previous_hash,
            }
            for key, value in dict(extra or {}).items():
                if key not in record and key not in {"hash", "signature"}:
                    record[key] = value
            record["hash"] = _record_hash(record)
            record["signature"] = _signature(secret, record["hash"])
            self._append_bytes(_canonical(record) + b"\n")
            if prefix is not None:
                # Only the bytes read and validated before this write are trusted.
                with _LOCKS_GUARD:
                    _PREFIXES[self.path] = prefix
                    if len(_PREFIXES) > _PREFIX_LIMIT:
                        _PREFIXES.popitem(last=False)
            return record

    def verify_integrity(
        self,
        *,
        require_signed_records: bool = False,
    ) -> bool:
        """Verify the chain, optionally requiring signed history."""
        with self._lock:
            try:
                secret = self._load_secret()
                if secret is None:
                    return not require_signed_records and (
                        not self.path.exists() or self.path.stat().st_size == 0
                    )
                sequence, _, _ = self._verified_tail(secret)
                return sequence > 0 if require_signed_records else True
            except (AuditLedgerError, OSError, ValueError, json.JSONDecodeError):
                return False

    def _verified_tail(
        self, secret: bytes, *, for_append: bool = False
    ) -> tuple[int, str, _VerifiedPrefix | None]:
        # The caller holds the path lock. Taking the entry out here means a
        # failed validation or write cannot publish an updated cache entry.
        cached = None
        if for_append:
            with _LOCKS_GUARD:
                cached = _PREFIXES.pop(self.path, None)
        if not self.path.exists():
            return 0, GENESIS_HASH, None
        try:
            data = self.path.read_bytes()
        except OSError as exc:
            raise AuditLedgerError(f"unable to read audit ledger: {exc}") from exc
        if not for_append:
            sequence, previous_hash = self._validate_lines(secret, data.splitlines())
            return sequence, previous_hash, None

        now = monotonic()
        key_digest = hashlib.sha256(secret).digest()
        expires_at = now + _PREFIX_LIFETIME
        offset = line_offset = sequence = 0
        previous_hash = GENESIS_HASH
        digest = hashlib.sha256()
        if (
            cached is not None
            and now < cached.expires_at
            and len(data) >= cached.size
            and hmac.compare_digest(key_digest, cached.key_digest)
        ):
            prefix_digest = hashlib.sha256(memoryview(data)[: cached.size])
            if hmac.compare_digest(prefix_digest.digest(), cached.digest):
                digest = prefix_digest
                offset, line_offset = cached.size, cached.line_count
                sequence, previous_hash = cached.sequence, cached.tail_hash
                expires_at = cached.expires_at

        suffix = data[offset:]
        lines = suffix.splitlines()
        sequence, previous_hash = self._validate_lines(
            secret, lines, sequence, previous_hash, line_offset
        )
        # LF (including CRLF) is an unambiguous splitlines boundary when more
        # bytes arrive. Cold validation retains the original legacy/EOF rules.
        prefix = None
        if sequence and data.endswith(b"\n"):
            digest.update(suffix)
            prefix = _VerifiedPrefix(
                len(data),
                digest.digest(),
                key_digest,
                line_offset + len(lines),
                sequence,
                previous_hash,
                expires_at,
            )
        return sequence, previous_hash, prefix

    @staticmethod
    def _validate_lines(
        secret: bytes,
        lines: list[bytes],
        sequence: int = 0,
        previous_hash: str = GENESIS_HASH,
        line_offset: int = 0,
    ) -> tuple[int, str]:
        legacy_digest = hashlib.sha256()
        signed_records_started = sequence > 0
        for line_number, raw_line in enumerate(lines, start=line_offset + 1):
            if not raw_line.strip():
                continue
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise AuditIntegrityError(
                    f"invalid JSON at audit line {line_number}"
                ) from exc
            if not isinstance(record, dict):
                raise AuditIntegrityError(f"invalid record at audit line {line_number}")
            if record.get("audit_version") != AUDIT_VERSION:
                if signed_records_started:
                    raise AuditIntegrityError(
                        "legacy record found after signed records"
                    )
                legacy_digest.update(raw_line.strip())
                legacy_digest.update(b"\n")
                continue

            if not signed_records_started:
                signed_records_started = True
                if legacy_digest.digest() != hashlib.sha256().digest():
                    previous_hash = f"legacy:{legacy_digest.hexdigest()}"
            sequence += 1
            if record.get("sequence") != sequence:
                raise AuditIntegrityError(
                    f"invalid sequence at audit line {line_number}"
                )
            if record.get("prev_hash") != previous_hash:
                raise AuditIntegrityError(f"broken chain at audit line {line_number}")
            actual_hash = record.get("hash")
            actual_signature = record.get("signature")
            if not isinstance(actual_hash, str) or not hmac.compare_digest(
                actual_hash, _record_hash(record)
            ):
                raise AuditIntegrityError(f"invalid hash at audit line {line_number}")
            if not isinstance(actual_signature, str) or not hmac.compare_digest(
                actual_signature, _signature(secret, actual_hash)
            ):
                raise AuditIntegrityError(
                    f"invalid signature at audit line {line_number}"
                )
            previous_hash = actual_hash

        if (
            not signed_records_started
            and legacy_digest.digest() != hashlib.sha256().digest()
        ):
            previous_hash = f"legacy:{legacy_digest.hexdigest()}"
        return sequence, previous_hash

    def _load_secret(self) -> bytes | None:
        configured = (
            os.getenv("AETHERRA_SECURITY_AUDIT_SECRET")
            or os.getenv("AETHERRA_SECURITY_STATE_SECRET")
            or ""
        ).strip()
        if configured:
            return configured.encode("utf-8")
        if not self.key_path.exists():
            return None
        try:
            secret = self.key_path.read_bytes().strip()
        except OSError as exc:
            raise AuditLedgerError(f"unable to read audit signing key: {exc}") from exc
        if len(secret) < 32:
            raise AuditLedgerError("audit signing key is invalid")
        return secret

    def _load_or_create_secret(self) -> bytes:
        secret = self._load_secret()
        if secret is not None:
            return secret
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        generated = secrets.token_urlsafe(48).encode("ascii")
        try:
            fd = os.open(self.key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            loaded = self._load_secret()
            if loaded is None:
                raise AuditLedgerError(
                    "audit signing key creation raced and failed"
                ) from exc
            return loaded
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(generated + b"\n")
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            with contextlib.suppress(OSError):
                self.key_path.unlink()
            raise
        return generated

    def _append_bytes(self, encoded: bytes) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            with os.fdopen(fd, "ab") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            with contextlib.suppress(OSError):
                os.chmod(self.path, 0o600)
        except OSError as exc:
            raise AuditLedgerError(f"unable to append audit record: {exc}") from exc


__all__ = [
    "AUDIT_VERSION",
    "AuditIntegrityError",
    "AuditLedgerError",
    "SecurityAuditLedger",
]
