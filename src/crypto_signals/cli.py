from .models import MarketSnapshot, Team
from .orchestrator import SignalOrchestrator
from .telegram import format_signal


def main() -> None:
    market = MarketSnapshot("BTCUSDT", "H1", 100000, 1.2, 1.4, .55, .42, .25, .95, sources=("demo",))
    engine = SignalOrchestrator()
    for team in Team:
        signal = engine.analyze(market, team)
        print(format_signal(signal) if signal else f"Tidak ada signal {team.value}.")


if __name__ == "__main__":
    main()
