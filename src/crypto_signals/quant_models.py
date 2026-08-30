"""Lightweight, dependency-free quantitative advisory models.

These models are risk diagnostics for signal ranking, not trading or execution.
They use explicit assumptions and fail closed on invalid input.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
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
        if not math.isfinite(win_probability) or not math.isfinite(payoff_ratio) or not 0 <= win_probability <= 1 or payoff_ratio <= 0:
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
        if not all(math.isfinite(value) for value in (win_probability, payoff_ratio, risk_fraction)) or not 0 <= win_probability <= 1 or payoff_ratio <= 0 or not 0 <= risk_fraction <= 1:
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
class BayesianWinRateResult:
    posterior_mean: float
    lower_bound: float
    upper_bound: float
    samples: int

class BayesianWinRate:
    """Conjugate Beta update; transparent adaptive win-rate estimate."""
    def __init__(self, prior_wins: float = 1.0, prior_losses: float = 1.0):
        if prior_wins <= 0 or prior_losses <= 0: raise ValueError("Beta priors must be positive")
        self.prior_wins, self.prior_losses = prior_wins, prior_losses

    def update(self, wins: int, losses: int) -> BayesianWinRateResult:
        if wins < 0 or losses < 0: raise ValueError("wins/losses cannot be negative")
        a, b = self.prior_wins + wins, self.prior_losses + losses
        mean = a / (a + b)
        variance = a * b / ((a + b) ** 2 * (a + b + 1))
        margin = 1.96 * variance ** .5
        return BayesianWinRateResult(mean, max(0.0, mean - margin), min(1.0, mean + margin), wins + losses)

class EWMAVolatility:
    """Exponentially weighted volatility estimate; no heavy numerical package."""
    def __init__(self, decay: float = .94):
        if not 0 < decay < 1: raise ValueError("decay must be between 0 and 1")
        self.decay = decay

    def estimate(self, returns: list[float]) -> float:
        if not returns or any(not math.isfinite(value) for value in returns): raise ValueError("returns must be finite and non-empty")
        variance = returns[0] ** 2
        for value in returns[1:]:
            variance = self.decay * variance + (1 - self.decay) * value ** 2
        return variance ** .5

class HistoricalVaR:
    """Historical lower-tail quantile of returns, expressed as a loss fraction."""
    def __init__(self, confidence: float = .95):
        if not 0 < confidence < 1: raise ValueError("confidence must be between 0 and 1")
        self.confidence = confidence

    def loss(self, returns: list[float]) -> float:
        if len(returns) < 20: raise ValueError("at least 20 returns are required")
        ordered = sorted(returns)
        index = max(0, min(len(ordered) - 1, int((1 - self.confidence) * len(ordered))))
        return max(0.0, -ordered[index])

class BootstrapInterval:
    """Seeded bootstrap interval for the mean return; diagnostic only."""
    def __init__(self, resamples: int = 500, seed: int = 11):
        if resamples < 100: raise ValueError("resamples must be >=100")
        self.resamples, self.seed = resamples, seed

    def mean_interval(self, returns: list[float]) -> tuple[float, float]:
        if not returns: raise ValueError("returns cannot be empty")
        rng, means = random.Random(self.seed), []
        for _ in range(self.resamples):
            sample = [returns[rng.randrange(len(returns))] for _ in returns]
            means.append(sum(sample) / len(sample))
        means.sort()
        return means[int(.025 * self.resamples)], means[int(.975 * self.resamples)]


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
