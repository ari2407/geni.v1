import pytest
from crypto_signals.discussion import DiscussionBus

def test_discussion_is_scoped_and_bounded():
    bus = DiscussionBus(2)
    bus.publish("spot_research", "spot", "evidence")
    bus.publish("leverage_research", "leverage", "evidence")
    assert len(bus.read("spot")) == 1
    with pytest.raises(ValueError): bus.publish("a", "spot", "x" * 4001)
