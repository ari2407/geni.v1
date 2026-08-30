import json
from crypto_signals.remote_adviser import RemoteAdviser

class Response:
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self): return json.dumps({"choices": [{"message": {"content": "research"}}]}).encode()

def test_remote_adviser_uses_https_style_api_without_tools(monkeypatch):
    captured = []
    monkeypatch.setattr("crypto_signals.remote_adviser.urlopen", lambda request, timeout: (captured.append(json.loads(request.data)) or Response()))
    result = RemoteAdviser("https://example.test/v1", "free-model").advise("researcher", {"symbol": "BTC/USDT"})
    assert result == "research"
    assert captured[0]["max_tokens"] == 300
    assert "tools" not in captured[0]
