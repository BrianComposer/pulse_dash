from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pygame  # noqa: E402

from pulse_dash.core.config import CONFIG  # noqa: E402
from pulse_dash.core.difficulty import DifficultyCurve  # noqa: E402
from pulse_dash.core.stages import StageGenerator  # noqa: E402
from pulse_dash.core.game import Game  # noqa: E402
from pulse_dash.states.playing import PlayingState  # noqa: E402


def main() -> None:
    pygame.init()

    generator = StageGenerator(seed=99)
    stage_1 = generator.generate(1)
    stage_4 = generator.generate(4)
    assert stage_1.length >= CONFIG.stage_base_length
    assert stage_4.length > stage_1.length
    assert len(stage_4.coins) >= len(stage_1.coins)
    assert stage_1.spikes == []

    early = DifficultyCurve(stage_index=1).snapshot(CONFIG.difficulty_warmup_seconds + 0.5)
    later_stage = DifficultyCurve(stage_index=5).snapshot(CONFIG.difficulty_warmup_seconds + 0.5)
    assert later_stage.normalized > early.normalized
    assert later_stage.spawn_interval < early.spawn_interval
    assert later_stage.gap_px < early.gap_px

    game = Game(headless=True)
    state = PlayingState(game)
    original_length = state.level.length
    state.player.rect.centerx = original_length + 10
    state.update(1 / 60)
    assert state.stage_index == 2
    assert state.level.length > original_length
    assert state.lives == CONFIG.start_lives
    assert state.coins == 0
    assert state.stage_coins == 0
    game.running = False
    pygame.quit()

    print("infinite_stages_test: OK")


if __name__ == "__main__":
    main()
