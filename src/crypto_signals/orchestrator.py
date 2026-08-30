from __future__ import annotations

from dataclasses import dataclass
from .agents import Agent, default_agents
from .models import AgentOpinion, MarketSnapshot, Signal, Team


@dataclass
class SignalOrchestrator:
    agents: list[Agent] | None = None
    min_confidence: float = .42

    def __post_init__(self):
        self.agents = self.agents or default_agents()

    def analyze(self, market: MarketSnapshot, team: Team) -> Signal | None:
        opinions = [agent.review(market, team) for agent in self.agents]
        validator = next(o for o in opinions if o.agent == "signal_validator")
        if validator.score < 0 or market.timeframe.upper() not in {"M5", "M15", "H1", "H4", "D1", "W1"}:
            return None
        usable = [o for o in opinions if o.agent not in {"candidate_screener", "data_quality"}]
        weighted = sum(o.score * o.confidence for o in usable) / max(sum(o.confidence for o in usable), .001)
        confidence = min(1.0, max(0.0, .5 + weighted * .5))
        if confidence < self.min_confidence or market.liquidity_score < .35:
            return None
        direction = "long" if weighted > .08 else "short" if weighted < -.08 else "neutral"
        if direction == "neutral":
            return None
        risk_pct = max(.005, min(.04, market.volatility * .035))
        stop = market.price * (1 - risk_pct if direction == "long" else 1 + risk_pct)
        targets = [market.price * (1 + risk_pct * n if direction == "long" else 1 - risk_pct * n) for n in (1.5, 2.5)]
        rr = 1.5
        if team is Team.LEVERAGE and market.volatility > .7:
            return None
        return Signal(market.symbol, team, direction, market.timeframe.upper(), market.price, stop, targets, confidence, rr, [o.rationale for o in opinions if abs(o.score) > .1], opinions, "paper")

    def self_review(self, signal: Signal) -> dict[str, float | str]:
        """A bounded review loop: report quality; never self-modifies or executes trades."""
        contradictions = sum(1 for o in signal.opinions if o.score * (1 if signal.direction == "long" else -1) < -.35)
        return {"status": "reviewed", "contradictions": contradictions, "confidence": signal.confidence, "action": "signal_only"}
