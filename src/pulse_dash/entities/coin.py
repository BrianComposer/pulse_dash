from __future__ import annotations

import math

import pygame

from pulse_dash.core.colors import ORANGE, WHITE, YELLOW
from pulse_dash.entities.base import Entity


class Coin(Entity):
    collected: bool = False
    phase: float = 0.0

    def update(self, dt: float) -> None:
        self.phase += dt * 8.0

    def draw(self, surface: pygame.Surface, camera_x: float) -> None:
        if self.collected:
            return
        r = self.rect.move(-int(camera_x), int(math.sin(self.phase) * 5))
        scale = abs(math.cos(self.phase))
        width = max(8, int(r.width * scale))
        coin_rect = pygame.Rect(0, 0, width, r.height)
        coin_rect.center = r.center
        pygame.draw.ellipse(surface, YELLOW, coin_rect)
        pygame.draw.ellipse(surface, WHITE, coin_rect, width=2)
        pygame.draw.line(surface, ORANGE, (coin_rect.centerx, coin_rect.top + 8), (coin_rect.centerx, coin_rect.bottom - 8), 2)
