"""Lightweight, dependency-free quantitative advisory models.

These models are risk diagnostics for signal ranking, not trading or execution.
They use explicit assumptions and fail closed on invalid input.
"""
from __future__ import annotations
from dataclasses import dataclass
import random

@dataclass(frozen=True)
class KellyResult:
    raw_fraction: float
    capped_fraction: float
    assumed_win_probability: float
    payoff_ratio: float

class KellyCriterion:
    def __init__(self, cap: float = .25):
        if not 0 < cap <= 1: raise ValueError("Kelly cap must be between 0 and 1")
        self.cap = cap

    def calculate(self, win_probability: float, payoff_ratio: float) -> KellyResult:
        if not 0 <= win_probability <= 1 or payoff_ratio <= 0:
            raise ValueError("invalid Kelly inputs")
        raw = win_probability - (1 - win_probability) / payoff_ratio
        return KellyResult(raw, max(0.0, min(self.cap, raw)), win_probability, payoff_ratio)

@dataclass(frozen=True)
class MonteCarloResult:
    trials: int
    steps: int
    ruin_probability: float
    p05_equity: float
    median_equity: float

class MonteCarloModel:
    def __init__(self, trials: int = 500, steps: int = 50, seed: int = 7):
        if trials < 100 or steps < 1: raise ValueError("Monte Carlo trials must be >=100 and steps >=1")
        self.trials, self.steps, self.seed = trials, steps, seed

    def simulate(self, win_probability: float, payoff_ratio: float, risk_fraction: float) -> MonteCarloResult:
        if not 0 <= win_probability <= 1 or payoff_ratio <= 0 or not 0 <= risk_fraction <= 1:
            raise ValueError("invalid Monte Carlo inputs")
        rng = random.Random(self.seed)
        outcomes = []
        ruined = 0
        for _ in range(self.trials):
            equity = 1.0
            for _ in range(self.steps):
                equity *= (1 + risk_fraction * payoff_ratio) if rng.random() < win_probability else (1 - risk_fraction)
                if equity <= 0: ruined += 1; break
            outcomes.append(equity)
        outcomes.sort()
        return MonteCarloResult(self.trials, self.steps, ruined / self.trials, outcomes[max(0, int(self.trials * .05) - 1)], outcomes[self.trials // 2])

@dataclass(frozen=True)
class QuantRiskResult:
    kelly: KellyResult
    monte_carlo: MonteCarloResult

class QuantRiskModel:
    def __init__(self, assumed_win_probability: float = .5):
        self.win_probability = assumed_win_probability
        self.kelly = KellyCriterion()
        self.monte_carlo = MonteCarloModel()

    def evaluate(self, payoff_ratio: float) -> QuantRiskResult:
        kelly = self.kelly.calculate(self.win_probability, payoff_ratio)
        # Use a fraction below full Kelly; this is an analytical stress test only.
        fraction = min(.05, kelly.capped_fraction)
        simulation = self.monte_carlo.simulate(self.win_probability, payoff_ratio, fraction)
        return QuantRiskResult(kelly, simulation)
