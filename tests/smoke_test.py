from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pulse_dash.core.game import Game  # noqa: E402
from pulse_dash.states.playing import PlayingState  # noqa: E402


def main() -> None:
    game = Game(headless=True)
    game.change_state(PlayingState(game))
    for _ in range(5):
        game.step(1 / 60)
    assert game.running is True
    assert game.screen.get_width() == 1280
    print("Smoke test passed: Pulse Dash initializes and advances frames correctly.")


if __name__ == "__main__":
    main()
