"""Governed agent/model ecosystem: proposals, promotion, rollback, and teams.

Agents may propose changes, but never self-install or self-execute changes. A
supervisor promotes only validated candidates and the core signal pipeline stays
available when ecosystem work is paused.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
from .models import Team

class Rank(IntEnum):
    RESERVE = 0
    AGENT = 1
    SENIOR = 2
    SUPERVISOR = 3
    TEAM_MANAGER = 4

@dataclass
class Proposal:
    proposer: str
    target: str
    change: str
    tests_passed: bool = False
    approved: bool = False
    rolled_back: bool = False

@dataclass
class EcosystemMember:
    name: str
    team: Team
    role: str
    rank: Rank = Rank.RESERVE
    score: float = 0.0
    consecutive_failures: int = 0
    proposals: list[Proposal] = field(default_factory=list)

class Ecosystem:
    def __init__(self, members: list[EcosystemMember], max_rank: Rank = Rank.SUPERVISOR):
        self.members = members
        self.max_rank = max_rank

    def propose(self, member: EcosystemMember, change: str) -> Proposal:
        proposal = Proposal(member.name, member.name, change)
        member.proposals.append(proposal)
        return proposal

    def promote(self, member: EcosystemMember, proposal: Proposal) -> bool:
        if proposal not in member.proposals or proposal.rolled_back or not proposal.tests_passed or not proposal.approved:
            return False
        if member.rank < self.max_rank:
            member.rank = Rank(member.rank + 1)
            member.consecutive_failures = 0
            return True
        return False

    def penalize(self, member: EcosystemMember, threshold: int = 3) -> EcosystemMember | None:
        member.consecutive_failures += 1
        member.score -= 1
        if member.consecutive_failures < threshold:
            return None
        member.rank = Rank(max(Rank.RESERVE, member.rank - 1))
        member.consecutive_failures = 0
        candidates = [x for x in self.members if x.team == member.team and x.role == member.role and x.rank == Rank.RESERVE and x is not member]
        if candidates:
            candidates[0].rank = Rank.AGENT
            return candidates[0]
        return None

    def rollback(self, proposal: Proposal) -> None:
        proposal.rolled_back = True
        proposal.approved = False
