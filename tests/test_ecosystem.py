from crypto_signals.ecosystem import Ecosystem, EcosystemMember, Rank
from crypto_signals.models import Team

def test_promotion_requires_test_and_approval():
    member = EcosystemMember("a", Team.SPOT, "research", Rank.AGENT)
    eco = Ecosystem([member])
    proposal = eco.propose(member, "improve prompt")
    assert not eco.promote(member, proposal)
    proposal.tests_passed = proposal.approved = True
    assert eco.promote(member, proposal)
    assert member.rank == Rank.SENIOR

def test_failure_promotes_reserve():
    active = EcosystemMember("active", Team.SPOT, "quant", Rank.AGENT)
    reserve = EcosystemMember("reserve", Team.SPOT, "quant", Rank.RESERVE)
    eco = Ecosystem([active, reserve])
    for _ in range(3): replacement = eco.penalize(active)
    assert replacement is reserve and reserve.rank == Rank.AGENT
