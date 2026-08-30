from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentScore:
    wins: int = 0
    losses: int = 0
    score: float = 0.0
    history: list[str] = field(default_factory=list)

    def settle(self, outcome: str, reward: float = 1.0, penalty: float = 1.0) -> None:
        if outcome == "tp":
            self.wins += 1
            self.score += reward
        elif outcome == "sl":
            self.losses += 1
            self.score -= penalty
        else:
            raise ValueError("outcome must be 'tp' or 'sl'")
        self.history.append(outcome)

    @property
    def win_rate(self) -> float:
        total = self.wins + self.losses
        return self.wins / total if total else 0.0
