"""Rate-limit-aware source contracts. Network clients are intentionally separate from agents."""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass
class SourceHealth:
    name: str
    remaining: int | None = None
    limit: int | None = None
    healthy: bool = True
    last_error: str | None = None
    blocked_until: float = 0.0
    failures: int = 0


class SourcePool:
    """Choose a healthy source before quota exhaustion and recover after errors."""

    def __init__(self, sources: list[SourceHealth], reserve: int = 1, failure_cooldown: float = 30.0):
        if reserve < 0:
            raise ValueError("reserve cannot be negative")
        self.sources = sources
        self.reserve = reserve
        self.failure_cooldown = failure_cooldown
        self._cursor = 0

    def next(self) -> SourceHealth | None:
        if not self.sources:
            return None
        now = monotonic()
        for offset in range(len(self.sources)):
            source = self.sources[(self._cursor + offset) % len(self.sources)]
            if now < source.blocked_until:
                continue
            if not source.healthy:
                # Transient failures are retried after a cool-off.
                source.healthy = True
            available = source.remaining is None or source.remaining > self.reserve
            if source.healthy and available:
                self._cursor = (self._cursor + offset + 1) % len(self.sources)
                return source
        return None

    def mark_failure(self, source: SourceHealth, error: str) -> None:
        source.healthy = False
        source.last_error = error
        source.failures += 1
        source.blocked_until = monotonic() + self.failure_cooldown

    def mark_rate_limited(self, source: SourceHealth, seconds: float = 60.0) -> None:
        source.blocked_until = monotonic() + max(0.0, seconds)
