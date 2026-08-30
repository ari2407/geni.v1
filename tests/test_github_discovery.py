import json
from io import BytesIO
from crypto_signals.github_discovery import discover_github

class Response:
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self): return json.dumps({"items": [{"full_name": "a/b", "html_url": "https://github.com/a/b", "stargazers_count": 20}]}).encode()

def test_github_discovery_is_metadata_only():
    result = discover_github(fetcher=lambda request, timeout: Response(), per_query=1)
    assert len(result) == 1
    assert result["https://github.com/a/b"]["stars"] == 20
