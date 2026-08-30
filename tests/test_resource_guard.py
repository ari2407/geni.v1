from crypto_signals.resource_guard import ResourceGuard

def test_resource_guard_returns_device_status(tmp_path):
    status = ResourceGuard().status(tmp_path)
    assert 0 <= status.disk_used <= 1
    assert isinstance(status.pause_upgrades, bool)
