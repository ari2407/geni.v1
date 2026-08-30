import argparse
import logging

from .scheduler import SchedulerConfig, SignalScheduler, install_shutdown_handlers
from .summary import DailySummaryAgent
from .state import PersistentState
from .telegram import telegram_emitter
from .universe import PublicUniverse
from .profiles import get_profile
from .remote_adviser import RemoteAdviser


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the signal-only crypto scheduler")
    parser.add_argument("--symbol", default="BTC/USDT", help="single pair; ignored with --all-public")
    parser.add_argument("--symbols", help="comma-separated pairs")
    parser.add_argument("--all-public", action="store_true", help="discover eligible public exchange pairs")
    parser.add_argument("--max-symbols", type=int, default=None, help="safety cap for --all-public")
    parser.add_argument("--profile", choices=["lite", "remote"], default="lite", help="lite is suitable for low-resource laptops")
    parser.add_argument("--timeframe", default="H1", choices=["M5", "M15", "H1", "H4", "D1"])
    parser.add_argument("--interval", type=int, default=300, help="seconds between cycles (minimum 5)")
    parser.add_argument("--cooldown", type=int, default=1800, help="seconds before identical signal may repeat")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--once", action="store_true", help="run one cycle and exit")
    parser.add_argument("--telegram", action="store_true", help="send approved signals and daily recap to Telegram")
    parser.add_argument("--state", default="data/runtime/state.db", help="SQLite state path for restart-safe cooldowns")
    args = parser.parse_args()
    profile = get_profile(args.profile)
    max_symbols = args.max_symbols or profile.max_symbols
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        emitter = telegram_emitter().send if args.telegram else print
        adviser = RemoteAdviser() if profile.llm_mode == "internet" else None
    except ValueError as exc:
        parser.error(str(exc))
    state = PersistentState(args.state)
    summary = DailySummaryAgent(emitter, state=state) if args.telegram else None
    scheduler = SignalScheduler(config=SchedulerConfig(args.interval, args.cooldown, args.retries), emitter=emitter, summary=summary, state=state, adviser=adviser)
    if args.all_public:
        if max_symbols < 1 or max_symbols > 1000:
            parser.error("--max-symbols must be between 1 and 1000")
        universe = PublicUniverse()
        symbols = universe.discover(max_symbols=max_symbols)
        if not symbols:
            parser.error("no public symbols discovered")
        # Refresh the top universe at every scheduler cycle so membership can change.
        symbol_source = lambda: universe.discover(max_symbols=max_symbols) or symbols
    elif args.symbols:
        symbols = [item.strip().upper() for item in args.symbols.split(",") if item.strip()]
        symbol_source = symbols
    else:
        symbols = [args.symbol.upper()]
        symbol_source = symbols
    if args.once:
        scheduler.run_symbols(symbols, args.timeframe)
        return
    stop = scheduler.stop_event()
    install_shutdown_handlers(stop)
    scheduler.run_forever(symbol_source, args.timeframe, stop)


if __name__ == "__main__":
    main()
