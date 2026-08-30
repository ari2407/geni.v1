"""Isolated active/reserve roster with auditable promotion and demotion."""
from __future__ import annotations
from dataclasses import dataclass, field
from .models import Team

ROLES = ("candidate_screener", "deep_researcher", "technical_analyst", "risk_manager", "signal_validator")

@dataclass
class AgentProfile:
    name: str
    role: str
    team: Team
    reserve: bool = False
    consecutive_losses: int = 0
    score: float = 0.0

@dataclass
class TeamRoster:
    team: Team
    active: dict[str, AgentProfile] = field(default_factory=dict)
    reserves: list[AgentProfile] = field(default_factory=list)
    penalty_limit: int = 3

    def __post_init__(self):
        for role in ROLES:
            self.active.setdefault(role, AgentProfile(f"{self.team.value}_{role}_01", role, self.team))
        if not self.reserves:
            self.reserves = [AgentProfile(f"{self.team.value}_reserve_{i:02d}", ROLES[i % len(ROLES)], self.team, True) for i in range(1, 6)]

    def record(self, agent_name: str, outcome: str) -> AgentProfile:
        agent = next((a for a in list(self.active.values()) + self.reserves if a.name == agent_name), None)
        if agent is None: raise KeyError(agent_name)
        if outcome == "tp":
            agent.score += 1; agent.consecutive_losses = 0
        elif outcome == "sl":
            agent.score -= 1; agent.consecutive_losses += 1
        else: raise ValueError("outcome must be tp or sl")
        if not agent.reserve and agent.consecutive_losses >= self.penalty_limit:
            self.demote(agent.role)
        return agent

    def demote(self, role: str) -> AgentProfile:
        old = self.active[role]
        old.reserve = True
        self.reserves.append(old)
        replacement = next((a for a in self.reserves if a.role == role and a.name != old.name), None)
        if replacement is None:
            replacement = self.reserves[0] if self.reserves else AgentProfile(f"{self.team.value}_{role}_recovery", role, self.team)
        self.reserves.remove(replacement)
        replacement.reserve = False
        replacement.consecutive_losses = 0
        self.active[role] = replacement
        return replacement

    def promote_next(self, role: str | None = None) -> AgentProfile | None:
        candidate = next((a for a in self.reserves if role is None or a.role == role), None)
        if not candidate: return None
        return self.demote(candidate.role) if role else self._promote_any(candidate)

    def _promote_any(self, candidate):
        return self.demote(candidate.role)

    def snapshot(self):
        return {"team": self.team.value, "active": {role: a.name for role, a in self.active.items()}, "reserves": [a.name for a in self.reserves]}
