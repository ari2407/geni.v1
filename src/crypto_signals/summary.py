from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from .state import PersistentState


@dataclass
class DailySummaryAgent:
    """Telegram-only summary role; it cannot read credentials or place orders."""
    sender: callable
    state: PersistentState | None = None
    sent_date: str | None = None
    stats: dict[str, int] = field(default_factory=lambda: {"spot": 0, "leverage": 0, "long": 0, "short": 0})

    def record(self, team: str, direction: str) -> None:
        if team not in {"spot", "leverage"} or direction not in {"long", "short"}:
            raise ValueError("invalid summary metric")
        self.stats[team] += 1
        self.stats[direction] += 1
        if self.state:
            day = datetime.now(timezone.utc).date().isoformat()
            self.state.record(day, team)
            self.state.record(day, direction)

    def maybe_send(self, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        day = now.date().isoformat()
        if now.hour < 23 or self.sent_date == day or (self.state and self.state.summary_was_sent(day)):
            return False
        stats = self.state.stats(day) if self.state else self.stats
        self.sender("📋 REKAP SIGNAL HARI INI\n\n"
                    f"Tanggal UTC: {day}\n"
                    f"Spot: {stats.get('spot', 0)} signal\n"
                    f"Leverage: {stats.get('leverage', 0)} signal\n"
                    f"Long: {stats.get('long', 0)} | Short: {stats.get('short', 0)}\n\n"
                    "Catatan: rekap signal, bukan hasil transaksi atau jaminan profit.")
        if self.state:
            self.state.mark_summary_sent(day)
        self.sent_date = day
        self.stats = {key: 0 for key in self.stats}
        return True
