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


class SourcePool:
    """Choose a healthy source before quota exhaustion; never spins forever."""

    def __init__(self, sources: list[SourceHealth], reserve: int = 1):
        self.sources = sources
        self.reserve = reserve
        self._cursor = 0

    def next(self) -> SourceHealth | None:
        if not self.sources:
            return None
        for offset in range(len(self.sources)):
            source = self.sources[(self._cursor + offset) % len(self.sources)]
            available = source.remaining is None or source.remaining > self.reserve
            if source.healthy and available:
                self._cursor = (self._cursor + offset + 1) % len(self.sources)
                return source
        return None

    def mark_failure(self, source: SourceHealth, error: str) -> None:
        source.healthy = False
        source.last_error = error
