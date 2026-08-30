from __future__ import annotations

from abc import ABC, abstractmethod
from .models import AgentOpinion, MarketSnapshot, Team


class Agent(ABC):
    name = "agent"

    @abstractmethod
    def review(self, market: MarketSnapshot, team: Team) -> AgentOpinion:
        raise NotImplementedError


class CandidateScreener(Agent):
    name = "candidate_screener"

    def review(self, m, team):
        score = min(1.0, max(0.0, m.liquidity_score * 0.7 + min(m.volume_ratio / 2, 1) * 0.3))
        return AgentOpinion(self.name, score, score, "Likuiditas dan volume diperiksa sebelum analisis tim.")


class RegimeAnalyst(Agent):
    name = "market_regime"

    def review(self, m, team):
        score = m.trend_score * 0.7 + m.momentum_score * 0.3
        return AgentOpinion(self.name, score, min(1, abs(score) + .35), f"Regime berdasarkan tren {m.trend_score:+.2f} dan momentum {m.momentum_score:+.2f}.")


class TechnicalAnalyst(Agent):
    name = "technical_structure"

    def review(self, m, team):
        score = m.trend_score * .55 + m.momentum_score * .45
        return AgentOpinion(self.name, score, min(1, .4 + abs(score) * .6), "Konfirmasi struktur harga dan momentum multi-timeframe diperlukan.")


class DataQualityAgent(Agent):
    name = "data_quality"

    def review(self, m, team):
        freshness = max(0, 1 - m.data_age_seconds / 900)
        score = freshness * m.liquidity_score
        return AgentOpinion(self.name, score, score, f"Data berumur {m.data_age_seconds} detik dari {len(m.sources)} sumber.")


class RiskManager(Agent):
    name = "risk_manager"

    def review(self, m, team):
        # Leverage is deliberately harder to approve than spot.
        safety = (1 - min(m.volatility, 1)) * m.liquidity_score
        threshold = .55 if team is Team.LEVERAGE else .35
        score = safety if safety >= threshold else -safety
        return AgentOpinion(self.name, score, safety, "Risiko volatilitas, likuiditas, dan kelayakan invalidation diperiksa.", {"safety": safety})


class NewsAndResearchAgent(Agent):
    name = "news_research"

    def review(self, m, team):
        # Connector-ready placeholder: no invented web data is allowed.
        return AgentOpinion(self.name, 0.0, .25, "Belum ada berita eksternal yang diberikan; tidak mengarang sentimen.", {"source_count": len(m.sources)})


class SignalValidator(Agent):
    name = "signal_validator"

    def review(self, m, team):
        valid_tf = m.timeframe.upper() in {"M5", "M15", "H1", "H4", "D1", "W1"}
        score = 1.0 if valid_tf and m.data_age_seconds <= 900 else -1.0
        return AgentOpinion(self.name, score, 1.0, "Validasi timeframe minimum M5 dan freshness data.")


def default_agents() -> list[Agent]:
    return [CandidateScreener(), RegimeAnalyst(), TechnicalAnalyst(), DataQualityAgent(), RiskManager(), NewsAndResearchAgent(), SignalValidator()]
