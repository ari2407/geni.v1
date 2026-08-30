from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Team(str, Enum):
    SPOT = "spot"
    LEVERAGE = "leverage"


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    timeframe: str
    price: float
    change_24h: float
    volume_ratio: float
    trend_score: float  # -1 bearish .. +1 bullish
    momentum_score: float  # -1 .. +1
    volatility: float
    liquidity_score: float  # 0 .. 1
    data_age_seconds: int = 0
    sources: tuple[str, ...] = ()


@dataclass
class AgentOpinion:
    agent: str
    score: float  # -1 .. +1
    confidence: float  # 0 .. 1
    rationale: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Signal:
    symbol: str
    team: Team
    direction: str
    timeframe: str
    entry: float
    stop_loss: float
    targets: list[float]
    confidence: float
    risk_reward: float
    reasons: list[str]
    opinions: list[AgentOpinion]
    status: str = "candidate"

    @property
    def invalidation(self) -> float:
        return self.stop_loss
