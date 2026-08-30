import os
from crypto_signals.live_scheduler import load_dotenv

def test_dotenv_loads_without_overriding_environment(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text('TEST_FREE_SIGNAL="hello"\nTEST_EXISTING=file\n')
    monkeypatch.setenv("TEST_EXISTING", "environment")
    load_dotenv(str(path))
    assert os.environ["TEST_FREE_SIGNAL"] == "hello"
    assert os.environ["TEST_EXISTING"] == "environment"
