"""Safe 24/7 polling loop for signal generation.

The scheduler is signal-only: its emitter receives text, and there is no order
execution path. It is deliberately dependency-free and easy to supervise.
"""
from __future__ import annotations

import logging
import signal
import threading
import time
from dataclasses import dataclass, field
from typing import Callable

from .live_data import LiveMarketData
from .models import Signal, Team
from .orchestrator import SignalOrchestrator
from .telegram import format_signal
from .summary import DailySummaryAgent

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class SchedulerConfig:
    interval_seconds: int = 300
    cooldown_seconds: int = 1800
    retries: int = 3
    retry_backoff_seconds: float = 2.0

    def __post_init__(self):
        if self.interval_seconds < 5:
            raise ValueError("interval_seconds must be at least 5")
        if self.cooldown_seconds < 0 or self.retries < 0 or self.retry_backoff_seconds < 0:
            raise ValueError("cooldown, retries, and backoff cannot be negative")


@dataclass
class SignalScheduler:
    data: LiveMarketData = field(default_factory=LiveMarketData)
    engine: SignalOrchestrator = field(default_factory=SignalOrchestrator)
    config: SchedulerConfig = field(default_factory=SchedulerConfig)
    emitter: Callable[[str], None] = print
    clock: Callable[[], float] = time.monotonic
    sleep: Callable[[float], None] = time.sleep
    summary: DailySummaryAgent | None = None
    _sent_at: dict[tuple, float] = field(default_factory=dict, init=False)

    def stop_event(self) -> threading.Event:
        return threading.Event()

    def _fetch_with_retry(self, symbol: str, timeframe: str):
        last_error = None
        for attempt in range(self.config.retries + 1):
            try:
                return self.data.fetch_snapshot(symbol, timeframe)
            except Exception as exc:
                last_error = exc
                if attempt < self.config.retries:
                    delay = self.config.retry_backoff_seconds * (2 ** attempt)
                    log.warning("data attempt %d failed: %s; retrying in %.1fs", attempt + 1, exc, delay)
                    self.sleep(delay)
        raise RuntimeError(f"data fetch failed after retries: {last_error}") from last_error

    def _key(self, signal: Signal) -> tuple:
        # Same asset/team/direction/timeframe is one logical signal. A reversal
        # is a different key and may be emitted immediately.
        return (signal.symbol, signal.team.value, signal.direction, signal.timeframe)

    def _allowed(self, signal: Signal, now: float) -> bool:
        previous = self._sent_at.get(self._key(signal))
        return previous is None or now - previous >= self.config.cooldown_seconds

    def _remember(self, signal: Signal, now: float) -> None:
        if self.config.cooldown_seconds == 0:
            return
        self._sent_at[self._key(signal)] = now
        self._sent_at = {k: t for k, t in self._sent_at.items() if now - t < self.config.cooldown_seconds}

    def run_cycle(self, symbol: str = "BTC/USDT", timeframe: str = "H1") -> list[Signal]:
        market = self._fetch_with_retry(symbol, timeframe)
        emitted: list[Signal] = []
        now = self.clock()
        for team in Team:
            candidate = self.engine.analyze(market, team)
            if candidate is None or not self._allowed(candidate, now):
                continue
            review = self.engine.self_review(candidate)
            if review["status"] != "reviewed" or review["action"] != "signal_only":
                continue
            self.emitter(format_signal(candidate))
            self._remember(candidate, now)  # only deduplicate after successful delivery
            if self.summary:
                self.summary.record(candidate.team.value, candidate.direction)
            emitted.append(candidate)
        if self.summary:
            self.summary.maybe_send()
        return emitted

    def run_symbols(self, symbols: list[str], timeframe: str = "H1") -> list[Signal]:
        emitted: list[Signal] = []
        for symbol in symbols:
            try:
                emitted.extend(self.run_cycle(symbol, timeframe))
            except Exception:
                log.exception("symbol cycle failed: %s", symbol)
        return emitted

    def run_forever(self, symbol: str | list[str] = "BTC/USDT", timeframe: str = "H1", stop: threading.Event | None = None) -> None:
        """Run until stop is set; Ctrl-C/TERM are handled by the CLI."""
        stop = stop or self.stop_event()
        log.info("scheduler started: %s %s every %ss", symbol, timeframe, self.config.interval_seconds)
        while not stop.is_set():
            started = self.clock()
            try:
                self.run_symbols(symbol, timeframe) if isinstance(symbol, list) else self.run_cycle(symbol, timeframe)
            except Exception:
                log.exception("cycle failed; scheduler remains alive")
            elapsed = max(0.0, self.clock() - started)
            stop.wait(max(0.0, self.config.interval_seconds - elapsed))
        log.info("scheduler stopped safely")


def install_shutdown_handlers(stop: threading.Event) -> None:
    def request_shutdown(signum, _frame):
        log.info("shutdown requested by signal %s", signum)
        stop.set()
    signal.signal(signal.SIGINT, request_shutdown)
    signal.signal(signal.SIGTERM, request_shutdown)
