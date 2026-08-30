"""Zero-install launcher for low-resource users.

Usage: python run_scheduler.py --help
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))
from crypto_signals.live_scheduler import main

if __name__ == "__main__":
    main()
