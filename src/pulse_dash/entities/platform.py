from __future__ import annotations

import pygame

from pulse_dash.core.colors import CYAN, PLATFORM, PURPLE
from pulse_dash.entities.base import Entity


class Platform(Entity):
    def draw(self, surface: pygame.Surface, camera_x: float) -> None:
        screen_rect = self.rect.move(-int(camera_x), 0)
        pygame.draw.rect(surface, PLATFORM, screen_rect, border_radius=8)
        pygame.draw.rect(surface, CYAN, screen_rect, width=2, border_radius=8)
        pygame.draw.line(surface, PURPLE, (screen_rect.left + 5, screen_rect.bottom - 5), (screen_rect.right - 5, screen_rect.bottom - 5), 2)
