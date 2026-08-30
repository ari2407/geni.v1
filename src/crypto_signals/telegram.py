"""Optional Telegram delivery for signal notifications only."""
from __future__ import annotations

import json
import os
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class TelegramNotifier:
    def __init__(self, token: str | None = None, chat_id: str | None = None, timeout: int = 10, retries: int = 2):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "").strip()
        self.timeout = timeout
        self.retries = retries
        if not self.token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")
        if any(char.isspace() for char in self.token):
            raise ValueError("TELEGRAM_BOT_TOKEN is invalid")

    def send(self, text: str) -> None:
        if not text.strip():
            raise ValueError("Telegram message cannot be empty")
        # Telegram accepts up to 4096 characters; split without losing content.
        chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            self._send_chunk(chunk)

    def _send_chunk(self, text: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        body = urlencode({"chat_id": self.chat_id, "text": text, "disable_web_page_preview": "true"}).encode()
        last_error = None
        for attempt in range(self.retries + 1):
            try:
                request = Request(url, data=body, method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"})
                with urlopen(request, timeout=self.timeout) as response:
                    result = json.loads(response.read())
                if not result.get("ok"):
                    raise RuntimeError(f"Telegram API rejected message: {result.get('description', 'unknown error')}")
                return
            except (HTTPError, URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
                last_error = exc
                if attempt < self.retries:
                    sleep(2 ** attempt)
        raise RuntimeError(f"Telegram delivery failed after retries: {last_error}") from last_error


def telegram_emitter() -> TelegramNotifier:
    """Build from environment variables; credentials never come from source files."""
    return TelegramNotifier()


def format_signal(signal) -> str:
    team = "SPOT" if signal.team.value == "spot" else "LEVERAGE LONG/SHORT"
    targets = " / ".join(f"{x:.6g}" for x in signal.targets)
    reasons = "\n".join(f"• {r}" for r in signal.reasons[:3])
    return (f"📊 SIGNAL {team}\n\n{signal.symbol} — {signal.direction.upper()}\n"
            f"TF: {signal.timeframe}\nEntry: {signal.entry:.6g}\nSL: {signal.stop_loss:.6g}\n"
            f"TP: {targets}\nConfidence: {signal.confidence:.0%} | R:R: {signal.risk_reward:.1f}\n\n"
            f"Alasan:\n{reasons}\n\n⚠️ Signal paper-trading, bukan eksekusi otomatis. Kelola risiko sendiri.")
