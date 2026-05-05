from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pulse_dash.core.config import CONFIG  # noqa: E402
from pulse_dash.core.game import Game  # noqa: E402
from pulse_dash.states.game_over import GameOverState  # noqa: E402
from pulse_dash.states.playing import PlayingState  # noqa: E402


def test_lives_absorb_damage_before_game_over() -> None:
    game = Game(headless=True)
    state = PlayingState(game)
    game.change_state(state)

    assert state.lives == CONFIG.start_lives
    state._take_damage()
    assert state.lives == CONFIG.start_lives - 1
    assert isinstance(game.state, PlayingState), "The first spike should not immediately end the game"

    state.player.invulnerability_timer = 0.0
    state._take_damage()
    assert state.lives == CONFIG.start_lives - 2
    assert isinstance(game.state, PlayingState)

    state.player.invulnerability_timer = 0.0
    state._take_damage()
    assert isinstance(game.state, GameOverState), "The game should end only when all lives are consumed"


def test_procedural_audio_calls_are_safe_in_headless_mode() -> None:
    game = Game(headless=True)
    game.audio.start_music()
    game.audio.update(1 / 60, 0.5)
    game.audio.play_jump()
    game.audio.play_coin()
    game.audio.play_damage()
    game.audio.play_finish()
    game.audio.stop_music()


if __name__ == "__main__":
    test_lives_absorb_damage_before_game_over()
    test_procedural_audio_calls_are_safe_in_headless_mode()
    print("Lives and audio tests passed: damage is non-lethal until lives reach zero and audio is CI-safe.")
