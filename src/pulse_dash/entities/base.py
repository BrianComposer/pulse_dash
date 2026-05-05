from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class Entity:
    rect: pygame.Rect
    active: bool = True

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface, camera_x: float) -> None:
        raise NotImplementedError
