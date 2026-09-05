from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Generic, TypeVar


T = TypeVar("T")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class CacheEntry(Generic[T]):
    value: T
    fetched_at: datetime
    expires_at: datetime


class TTLCache(Generic[T]):
    """Small process-local cache that retains expired last-known-good values."""

    def __init__(self, clock: Callable[[], datetime] = utc_now):
        self._clock = clock
        self._entries: dict[str, CacheEntry[T]] = {}
        self._lock = RLock()

    def put(self, key: str, value: T, ttl_seconds: int) -> CacheEntry[T]:
        fetched_at = self._clock()
        entry = CacheEntry(
            value=value,
            fetched_at=fetched_at,
            expires_at=fetched_at + timedelta(seconds=ttl_seconds),
        )
        with self._lock:
            self._entries[key] = entry
        return entry

    def get_fresh(self, key: str) -> CacheEntry[T] | None:
        with self._lock:
            entry = self._entries.get(key)
        if entry is None or entry.expires_at <= self._clock():
            return None
        return entry

    def get_last_known_good(self, key: str) -> CacheEntry[T] | None:
        with self._lock:
            return self._entries.get(key)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
