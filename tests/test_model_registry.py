from crypto_signals.model_registry import enabled_models

def test_local_baseline_is_always_available():
    assert any(model.name == "local_rules" for model in enabled_models())
    assert all(model.role != "execution" for model in enabled_models())
