"""Small SQLite state store for restart-safe deduplication and daily audit data."""
from __future__ import annotations
import sqlite3
import threading
from pathlib import Path

class PersistentState:
    def __init__(self, path: str | Path = "data/runtime/state.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS sent_signals (key TEXT PRIMARY KEY, sent_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS daily_stats (day TEXT NOT NULL, metric TEXT NOT NULL, value INTEGER NOT NULL, PRIMARY KEY(day, metric));
            CREATE TABLE IF NOT EXISTS summary_sent (day TEXT PRIMARY KEY);
            """)

    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def allowed(self, key: str, now: float, cooldown: int) -> bool:
        with self._lock, self._connect() as db:
            row = db.execute("SELECT sent_at FROM sent_signals WHERE key=?", (key,)).fetchone()
            return row is None or now - row[0] >= cooldown

    def remember(self, key: str, now: float) -> None:
        with self._lock, self._connect() as db:
            db.execute("INSERT OR REPLACE INTO sent_signals(key,sent_at) VALUES(?,?)", (key, now))
            db.execute("DELETE FROM sent_signals WHERE sent_at < ?", (now - 86400 * 7,))

    def record(self, day: str, metric: str) -> None:
        with self._lock, self._connect() as db:
            db.execute("INSERT INTO daily_stats(day,metric,value) VALUES(?,?,1) ON CONFLICT(day,metric) DO UPDATE SET value=value+1", (day, metric))

    def stats(self, day: str) -> dict[str, int]:
        with self._lock, self._connect() as db:
            rows = db.execute("SELECT metric,value FROM daily_stats WHERE day=?", (day,)).fetchall()
        return {metric: value for metric, value in rows}

    def summary_was_sent(self, day: str) -> bool:
        with self._lock, self._connect() as db:
            return db.execute("SELECT 1 FROM summary_sent WHERE day=?", (day,)).fetchone() is not None

    def mark_summary_sent(self, day: str) -> None:
        with self._lock, self._connect() as db:
            db.execute("INSERT OR IGNORE INTO summary_sent(day) VALUES(?)", (day,))
