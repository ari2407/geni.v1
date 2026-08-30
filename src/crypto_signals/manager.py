"""Critical final approval gate for both teams."""
from .models import Signal

class CriticalManager:
    def approve(self, signal: Signal) -> tuple[bool, str]:
        if signal.direction not in {"long", "short"}:
            return False, "direction is neutral or invalid"
        if not 0.0 <= signal.confidence <= 1.0 or signal.confidence < .42:
            return False, "confidence below minimum"
        if signal.entry <= 0 or signal.stop_loss <= 0 or not signal.targets:
            return False, "invalid price levels"
        if signal.risk_reward < 1.0:
            return False, "risk reward below minimum"
        same_side = 1 if signal.direction == "long" else -1
        contradictions = sum(1 for opinion in signal.opinions if opinion.score * same_side < -.35)
        if contradictions >= 3:
            return False, "too many agent contradictions"
        return True, "approved"
