from __future__ import annotations

import argparse

from pulse_dash.core.game import Game


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Pulse Dash, a Pygame rhythm platformer.")
    parser.add_argument("--headless", action="store_true", help="Run using SDL dummy drivers. Useful for smoke tests.")
    args = parser.parse_args()
    game = Game(headless=args.headless)
    game.run()


if __name__ == "__main__":
    main()
