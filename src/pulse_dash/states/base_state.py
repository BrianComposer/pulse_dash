from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from pulse_dash.core.input import InputState

if TYPE_CHECKING:
    from pulse_dash.core.game import Game


class BaseState:
    def __init__(self, game: "Game") -> None:
        self.game = game

    def enter(self) -> None:
        pass

    def handle_input(self, input_state: InputState) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass
