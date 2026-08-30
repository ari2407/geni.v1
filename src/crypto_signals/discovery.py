"""Registry and selection of external candidates.

This module intentionally does not execute arbitrary remote code. Discovery is
metadata-first: candidates are reviewed, grouped, licensed, and selected before
an adapter is enabled.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CandidateGroup(str, Enum):
    DATA = "data"
    TECHNICAL = "technical"
    SENTIMENT = "sentiment"
    BACKTEST = "backtest"
    ORCHESTRATION = "orchestration"


@dataclass(frozen=True)
class Candidate:
    name: str
    url: str
    group: CandidateGroup
    license: str
    signal_only_fit: float
    maintenance_risk: float
    roles: tuple[str, ...]
    notes: str = ""

    @property
    def score(self) -> float:
        return round(self.signal_only_fit * (1 - self.maintenance_risk), 3)


CATALOG: tuple[Candidate, ...] = (
    Candidate("CCXT", "https://github.com/ccxt/ccxt", CandidateGroup.DATA, "MIT", .95, .10, ("exchange_data", "market_discovery"), "Unified public exchange data adapter."),
    Candidate("Freqtrade", "https://github.com/freqtrade/freqtrade", CandidateGroup.BACKTEST, "GPL-3.0", .75, .15, ("backtest", "paper_evaluation", "risk"), "Use only research/backtest surfaces; execution stays disabled."),
    Candidate("CryptoSignal", "https://github.com/CryptoSignal/Crypto-Signal", CandidateGroup.TECHNICAL, "MIT", .70, .65, ("technical",), "Older project; review before adapter work."),
    Candidate("Crypto Sentiment Bot", "https://github.com/CyberPunkMetalHead/Cryptocurrency-Sentiment-Bot", CandidateGroup.SENTIMENT, "review", .55, .60, ("sentiment",), "Reference only until license and activity are verified."),
    Candidate("LangGraph", "https://github.com/langchain-ai/langgraph", CandidateGroup.ORCHESTRATION, "MIT", .90, .20, ("workflow", "review_loop"), "Deterministic stateful orchestration option."),
    Candidate("CrewAI", "https://github.com/crewAIInc/crewAI", CandidateGroup.ORCHESTRATION, "MIT", .85, .20, ("role_agents", "workflow"), "Role-based orchestration option; not a market-data source."),
)


def group_candidates(candidates: tuple[Candidate, ...] = CATALOG) -> dict[CandidateGroup, list[Candidate]]:
    result = {group: [] for group in CandidateGroup}
    for candidate in candidates:
        result[candidate.group].append(candidate)
    for group in result:
        result[group].sort(key=lambda item: item.score, reverse=True)
    return result


def select_candidates(minimum_per_group: int = 1) -> list[Candidate]:
    """Select safe research candidates, preserving diversity across groups."""
    selected: list[Candidate] = []
    for group in group_candidates().values():
        selected.extend(group[:minimum_per_group])
    return sorted(selected, key=lambda item: item.score, reverse=True)
