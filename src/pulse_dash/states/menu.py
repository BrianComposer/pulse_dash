from __future__ import annotations

import math

import pygame

from pulse_dash.core.colors import CYAN, MAGENTA, MUTED, WHITE, YELLOW
from pulse_dash.core.config import CONFIG
from pulse_dash.core.input import InputState
from pulse_dash.core.utils import draw_text, draw_vertical_gradient
from pulse_dash.states.base_state import BaseState


class MenuState(BaseState):
    time: float = 0.0

    def handle_input(self, input_state: InputState) -> None:
        if input_state.confirm_pressed:
            from pulse_dash.states.playing import PlayingState

            self.game.change_state(PlayingState(self.game))
        elif input_state.pause_pressed or input_state.quit_requested:
            self.game.running = False

    def update(self, dt: float) -> None:
        self.time += dt

    def draw(self, surface: pygame.Surface) -> None:
        draw_vertical_gradient(surface, (10, 6, 34), (3, 3, 12))
        cx, cy = CONFIG.width // 2, CONFIG.height // 2
        for i in range(18):
            angle = self.time * 0.7 + i * 0.55
            radius = 190 + math.sin(self.time + i) * 34
            pos = (int(cx + math.cos(angle) * radius), int(cy + math.sin(angle * 1.3) * radius * 0.45))
            pygame.draw.circle(surface, (*CYAN, 80), pos, 2 + i % 5)
        draw_text(surface, "PULSE DASH", self.game.assets.font_title, WHITE, (cx, 185))
        draw_text(surface, "un arcade geométrico en Python + Pygame", self.game.assets.font_medium, CYAN, (cx, 250))
        draw_text(surface, "ESPACIO / ENTER para empezar", self.game.assets.font_large, YELLOW, (cx, 390))
        draw_text(surface, "Salta, evita pinchos, recoge monedas y llega al final.", self.game.assets.font_medium, MUTED, (cx, 450))
        draw_text(surface, "Controles: espacio o ↑ para saltar · P/Esc pausa · R reinicia", self.game.assets.font_small, MAGENTA, (cx, 610))
