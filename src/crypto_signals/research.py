"""Deep-research role contract. It consumes fetched public evidence, never invents it."""
from dataclasses import dataclass
from .models import MarketSnapshot, Team


@dataclass(frozen=True)
class ResearchEvidence:
    source: str
    title: str
    url: str
    published_at: str | None = None
    confidence: float = .0


class DeepResearchAgent:
    name = "deep_researcher"

    def review(self, market: MarketSnapshot, team: Team, evidence: list[ResearchEvidence] | None = None) -> dict:
        evidence = evidence or []
        return {
            "agent": self.name,
            "team": team.value,
            "symbol": market.symbol,
            "evidence_count": len(evidence),
            "sources": [item.source for item in evidence],
            "status": "no_external_evidence" if not evidence else "evidence_attached",
            "rationale": "Tidak ada data eksternal yang diberikan; agent tidak mengarang berita atau sentimen." if not evidence else "Bukti publik dilampirkan untuk ditinjau.",
        }
