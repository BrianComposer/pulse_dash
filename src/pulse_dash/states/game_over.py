from __future__ import annotations

import pygame

from pulse_dash.core.colors import CYAN, GREEN, MAGENTA, MUTED, RED, WHITE, YELLOW
from pulse_dash.core.config import CONFIG
from pulse_dash.core.input import InputState
from pulse_dash.core.utils import draw_text, draw_vertical_gradient, rounded_panel
from pulse_dash.states.base_state import BaseState


class GameOverState(BaseState):
    def __init__(
        self,
        game,
        won: bool,
        score: int,
        coins: int,
        progress: int,
        *,
        stage: int = 1,
        total_time: float = 0.0,
    ) -> None:
        super().__init__(game)
        self.won = won
        self.score = score
        self.coins = coins
        self.progress = progress
        self.stage = stage
        self.total_time = total_time

    def handle_input(self, input_state: InputState) -> None:
        if input_state.restart_pressed or input_state.confirm_pressed:
            from pulse_dash.states.playing import PlayingState

            self.game.change_state(PlayingState(self.game))
        elif input_state.pause_pressed or input_state.quit_requested:
            from pulse_dash.states.menu import MenuState

            self.game.change_state(MenuState(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        draw_vertical_gradient(surface, (10, 6, 34), (3, 3, 12))
        panel = pygame.Rect(CONFIG.width // 2 - 315, CONFIG.height // 2 - 205, 630, 410)
        rounded_panel(surface, panel, (15, 19, 42), CYAN if self.won else RED)
        title = "RUN COMPLETADA" if self.won else "CRASH GEOMÉTRICO"
        title_color = GREEN if self.won else RED
        minutes = int(self.total_time // 60)
        seconds = int(self.total_time % 60)
        draw_text(surface, title, self.game.assets.font_large, title_color, (CONFIG.width // 2, panel.top + 62))
        draw_text(surface, f"Stage alcanzado: {self.stage}", self.game.assets.font_medium, GREEN, (CONFIG.width // 2, panel.top + 128))
        draw_text(surface, f"Puntuación: {self.score}", self.game.assets.font_medium, WHITE, (CONFIG.width // 2, panel.top + 174))
        draw_text(surface, f"Monedas totales: {self.coins}", self.game.assets.font_medium, YELLOW, (CONFIG.width // 2, panel.top + 218))
        draw_text(surface, f"Tiempo: {minutes:02d}:{seconds:02d} · Progreso stage actual: {self.progress}%", self.game.assets.font_medium, MAGENTA, (CONFIG.width // 2, panel.top + 262))
        draw_text(surface, "ENTER / R para nueva run infinita", self.game.assets.font_medium, CYAN, (CONFIG.width // 2, panel.top + 326))
        draw_text(surface, "ESC para volver al menú", self.game.assets.font_small, MUTED, (CONFIG.width // 2, panel.top + 362))
