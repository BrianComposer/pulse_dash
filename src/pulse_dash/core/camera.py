from __future__ import annotations

from dataclasses import dataclass

import pygame

from pulse_dash.core.config import CONFIG
from pulse_dash.core.utils import lerp


@dataclass
class Camera:
    x: float = 0.0
    shake_timer: float = 0.0
    shake_intensity: float = 0.0

    def update(self, target_rect: pygame.Rect, dt: float) -> None:
        desired = max(0.0, target_rect.centerx - CONFIG.camera_dead_zone_x)
        self.x = lerp(self.x, desired, min(1.0, dt * 5.0))
        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)

    def world_to_screen(self, rect: pygame.Rect) -> pygame.Rect:
        offset = self.current_offset()
        return rect.move(-int(self.x) + offset[0], offset[1])

    def current_offset(self) -> tuple[int, int]:
        if self.shake_timer <= 0:
            return 0, 0
        import random

        strength = self.shake_intensity * (self.shake_timer / max(0.001, self.shake_timer + 0.1))
        return random.randint(-int(strength), int(strength)), random.randint(-int(strength), int(strength))

    def shake(self, duration: float = 0.18, intensity: float = 7.0) -> None:
        self.shake_timer = duration
        self.shake_intensity = intensity
