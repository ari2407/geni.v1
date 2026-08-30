import json
from io import BytesIO

import pytest

from crypto_signals.telegram import TelegramNotifier


class FakeResponse:
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self): return json.dumps({"ok": True}).encode()


def test_missing_telegram_credentials_are_rejected(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    with pytest.raises(ValueError):
        TelegramNotifier()


def test_message_is_posted_without_exposing_secret(monkeypatch):
    calls = []
    monkeypatch.setattr("crypto_signals.telegram.urlopen", lambda request, timeout: (calls.append((request.full_url, request.data)) or FakeResponse()))
    notifier = TelegramNotifier("secret-token", "123", retries=0)
    notifier.send("hello signal")
    assert len(calls) == 1
    assert "secret-token" in calls[0][0]
    assert b"hello+signal" in calls[0][1]


def test_long_message_is_split(monkeypatch):
    calls = []
    monkeypatch.setattr("crypto_signals.telegram.urlopen", lambda request, timeout: (calls.append(request) or FakeResponse()))
    TelegramNotifier("token", "123", retries=0).send("x" * 8001)
    assert len(calls) == 3
