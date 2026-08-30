"""One bounded live cycle: fetch public data, analyze, print Telegram text."""
from .live_data import LiveMarketData
from .models import Team
from .orchestrator import SignalOrchestrator
from .telegram import format_signal


def run_once(symbol: str = "BTC/USDT", timeframe: str = "H1") -> list[str]:
    market = LiveMarketData().fetch_snapshot(symbol, timeframe)
    engine = SignalOrchestrator()
    messages = []
    for team in Team:
        signal = engine.analyze(market, team)
        if signal:
            engine.self_review(signal)
            messages.append(format_signal(signal))
    return messages


def main() -> None:
    try:
        messages = run_once()
    except (RuntimeError, ValueError) as exc:
        print(f"Data live belum tersedia: {exc}")
        print("Tidak ada signal yang dibuat dan tidak ada transaksi yang dijalankan.")
        return
    if not messages:
        print("Tidak ada signal yang memenuhi validasi saat ini.")
    for message in messages:
        print(message)


if __name__ == "__main__":
    main()
