"""Critical final approval gate for both teams."""
from .models import Signal
from .quant_models import QuantRiskModel


class CriticalManager:
    def __init__(self, quant_model: QuantRiskModel | None = None):
        self.quant_model = quant_model or QuantRiskModel()

    def approve(self, signal: Signal) -> tuple[bool, str]:
        if signal.direction not in {"long", "short"}:
            return False, "direction is neutral or invalid"
        if not 0.0 <= signal.confidence <= 1.0 or signal.confidence < .42:
            return False, "confidence below minimum"
        if signal.entry <= 0 or signal.stop_loss <= 0 or not signal.targets:
            return False, "invalid price levels"
        if signal.risk_reward < 1.0:
            return False, "risk reward below minimum"
        try:
            quant = self.quant_model.evaluate(signal.risk_reward)
            if quant.kelly.capped_fraction <= 0 or quant.monte_carlo.p05_equity <= 0:
                return False, "Kelly/Monte Carlo risk diagnostic failed"
        except (TypeError, ValueError, ArithmeticError):
            return False, "quantitative risk diagnostic unavailable"
        same_side = 1 if signal.direction == "long" else -1
        contradictions = sum(1 for opinion in signal.opinions if opinion.score * same_side < -.35)
        if contradictions >= 3:
            return False, "too many agent contradictions"
        return True, "approved"
