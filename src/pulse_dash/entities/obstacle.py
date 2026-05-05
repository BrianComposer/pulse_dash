from __future__ import annotations

import pygame

from pulse_dash.core.colors import ORANGE, RED, WHITE
from pulse_dash.entities.base import Entity


class Spike(Entity):
    def draw(self, surface: pygame.Surface, camera_x: float) -> None:
        r = self.rect.move(-int(camera_x), 0)
        points = [(r.centerx, r.top), (r.right, r.bottom), (r.left, r.bottom)]
        pygame.draw.polygon(surface, RED, points)
        inset = 8
        inner = [(r.centerx, r.top + inset), (r.right - inset, r.bottom - 4), (r.left + inset, r.bottom - 4)]
        pygame.draw.polygon(surface, ORANGE, inner, width=3)
        pygame.draw.line(surface, WHITE, (r.centerx, r.top + 13), (r.centerx, r.centery + 8), 2)
