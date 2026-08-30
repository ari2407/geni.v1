import pytest
from crypto_signals.profiles import get_profile

def test_lite_profile_has_small_safe_defaults():
    profile = get_profile()
    assert profile.max_symbols == 20
    assert profile.llm_mode == "off"

def test_unknown_profile_rejected():
    with pytest.raises(ValueError): get_profile("unknown")
