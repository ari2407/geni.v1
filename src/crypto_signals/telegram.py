from .models import Signal


def format_signal(signal: Signal) -> str:
    team = "SPOT" if signal.team.value == "spot" else "LEVERAGE LONG/SHORT"
    targets = " / ".join(f"{x:.6g}" for x in signal.targets)
    reasons = "\n".join(f"• {r}" for r in signal.reasons[:3])
    return (f"📊 SIGNAL {team}\n\n{signal.symbol} — {signal.direction.upper()}\n"
            f"TF: {signal.timeframe}\nEntry: {signal.entry:.6g}\nSL: {signal.stop_loss:.6g}\n"
            f"TP: {targets}\nConfidence: {signal.confidence:.0%} | R:R: {signal.risk_reward:.1f}\n\n"
            f"Alasan:\n{reasons}\n\n⚠️ Signal paper-trading, bukan eksekusi otomatis. Kelola risiko sendiri.")
