import argparse
import logging

from .scheduler import SchedulerConfig, SignalScheduler, install_shutdown_handlers


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the signal-only crypto scheduler")
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--timeframe", default="H1", choices=["M5", "M15", "H1", "H4", "D1"])
    parser.add_argument("--interval", type=int, default=300, help="seconds between cycles (minimum 5)")
    parser.add_argument("--cooldown", type=int, default=1800, help="seconds before identical signal may repeat")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--once", action="store_true", help="run one cycle and exit")
    parser.add_argument("--telegram", action="store_true", help="send approved signals to Telegram")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        emitter = telegram_emitter().send if args.telegram else print
    except ValueError as exc:
        parser.error(str(exc))
    scheduler = SignalScheduler(config=SchedulerConfig(args.interval, args.cooldown, args.retries), emitter=emitter)
    if args.once:
        scheduler.run_cycle(args.symbol, args.timeframe)
        return
    stop = scheduler.stop_event()
    install_shutdown_handlers(stop)
    scheduler.run_forever(args.symbol, args.timeframe, stop)


if __name__ == "__main__":
    main()
