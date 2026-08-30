from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class DailySummaryAgent:
    """Telegram-only summary role; it cannot read credentials or place orders."""
    sender: callable
    sent_date: str | None = None
    stats: dict[str, int] = field(default_factory=lambda: {"spot": 0, "leverage": 0, "long": 0, "short": 0})

    def record(self, team: str, direction: str) -> None:
        self.stats[team] += 1
        self.stats[direction] += 1

    def maybe_send(self, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        day = now.date().isoformat()
        if now.hour < 23 or self.sent_date == day:
            return False
        self.sender("📋 REKAP SIGNAL HARI INI\n\n"
                    f"Tanggal UTC: {day}\n"
                    f"Spot: {self.stats['spot']} signal\n"
                    f"Leverage: {self.stats['leverage']} signal\n"
                    f"Long: {self.stats['long']} | Short: {self.stats['short']}\n\n"
                    "Catatan: rekap signal, bukan hasil transaksi atau jaminan profit.")
        self.sent_date = day
        self.stats = {key: 0 for key in self.stats}
        return True
