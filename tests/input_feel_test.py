from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import pygame  # noqa: E402

from pulse_dash.core.config import CONFIG  # noqa: E402
from pulse_dash.entities.player import Player  # noqa: E402


def test_buffered_jump_on_landing() -> None:
    pygame.init()
    player = Player.create(120, CONFIG.ground_y - 48 - 7)
    platform = pygame.Rect(0, CONFIG.ground_y, 900, 46)
    player.on_ground = False
    player.velocity.y = 500
    player.request_jump(pressed=True, held=False)
    player.update(1 / 60, [platform])
    assert player.jumped_this_frame, "Buffered SPACE press should jump as soon as landing is detected"
    assert player.velocity.y == CONFIG.jump_velocity
    pygame.quit()


def test_coyote_jump_after_leaving_platform() -> None:
    pygame.init()
    player = Player.create(120, CONFIG.ground_y - 48)
    player.on_ground = True
    player.update(1 / 60, [])
    player.request_jump(pressed=True, held=False)
    player.update(1 / 60, [])
    assert player.jumped_this_frame, "SPACE should still jump briefly after leaving a platform"
    assert player.velocity.y < 0, "Coyote jump should produce upward velocity"
    pygame.quit()


if __name__ == "__main__":
    test_buffered_jump_on_landing()
    test_coyote_jump_after_leaving_platform()
    print("Input feel tests passed: jump buffer and coyote time are active.")
