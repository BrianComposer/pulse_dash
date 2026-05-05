from __future__ import annotations

import pygame

from pulse_dash.core.colors import CYAN, GREEN, MAGENTA, MUTED, RED, WHITE, YELLOW
from pulse_dash.core.config import CONFIG
from pulse_dash.core.input import InputState
from pulse_dash.core.utils import draw_text, draw_vertical_gradient, rounded_panel
from pulse_dash.states.base_state import BaseState


class GameOverState(BaseState):
    def __init__(self, game, won: bool, score: int, coins: int, progress: int) -> None:
        super().__init__(game)
        self.won = won
        self.score = score
        self.coins = coins
        self.progress = progress

    def handle_input(self, input_state: InputState) -> None:
        if input_state.restart_pressed or input_state.confirm_pressed:
            from pulse_dash.states.playing import PlayingState

            self.game.change_state(PlayingState(self.game))
        elif input_state.pause_pressed or input_state.quit_requested:
            from pulse_dash.states.menu import MenuState

            self.game.change_state(MenuState(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        draw_vertical_gradient(surface, (10, 6, 34), (3, 3, 12))
        panel = pygame.Rect(CONFIG.width // 2 - 285, CONFIG.height // 2 - 185, 570, 370)
        rounded_panel(surface, panel, (15, 19, 42), CYAN if self.won else RED)
        title = "NIVEL COMPLETADO" if self.won else "CRASH GEOMÉTRICO"
        title_color = GREEN if self.won else RED
        draw_text(surface, title, self.game.assets.font_large, title_color, (CONFIG.width // 2, panel.top + 70))
        draw_text(surface, f"Puntuación: {self.score}", self.game.assets.font_medium, WHITE, (CONFIG.width // 2, panel.top + 145))
        draw_text(surface, f"Monedas: {self.coins}", self.game.assets.font_medium, YELLOW, (CONFIG.width // 2, panel.top + 190))
        draw_text(surface, f"Progreso: {self.progress}%", self.game.assets.font_medium, MAGENTA, (CONFIG.width // 2, panel.top + 235))
        draw_text(surface, "ENTER / R para reiniciar", self.game.assets.font_medium, CYAN, (CONFIG.width // 2, panel.top + 300))
        draw_text(surface, "ESC para volver al menú", self.game.assets.font_small, MUTED, (CONFIG.width // 2, panel.top + 335))
