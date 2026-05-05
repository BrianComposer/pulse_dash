from __future__ import annotations

from dataclasses import dataclass

import pygame

from pulse_dash.core.colors import CYAN, MAGENTA, WHITE
from pulse_dash.core.config import CONFIG


@dataclass
class Player:
    rect: pygame.Rect
    velocity: pygame.Vector2
    on_ground: bool = False
    rotation: float = 0.0
    alive: bool = True

    @classmethod
    def create(cls, x: int = 120, y: int | None = None) -> "Player":
        size = 48
        initial_y = y if y is not None else CONFIG.ground_y - size
        return cls(rect=pygame.Rect(x, initial_y, size, size), velocity=pygame.Vector2(CONFIG.player_speed, 0))

    def jump(self) -> None:
        if self.on_ground and self.alive:
            self.velocity.y = CONFIG.jump_velocity
            self.on_ground = False

    def update(self, dt: float, platforms: list[pygame.Rect]) -> None:
        if not self.alive:
            return
        self.velocity.x = CONFIG.player_speed
        self.velocity.y += CONFIG.gravity * dt
        self.rect.x += int(self.velocity.x * dt)
        self.rect.y += int(self.velocity.y * dt)
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform) and self.velocity.y >= 0:
                previous_bottom = self.rect.bottom - int(self.velocity.y * dt)
                if previous_bottom <= platform.top + 10:
                    self.rect.bottom = platform.top
                    self.velocity.y = 0
                    self.on_ground = True

        if self.rect.top > CONFIG.height + 160:
            self.alive = False

        if not self.on_ground:
            self.rotation = (self.rotation + 420 * dt) % 360
        else:
            self.rotation = round(self.rotation / 90) * 90

    def draw(self, surface: pygame.Surface, camera_x: float) -> None:
        player_surface = pygame.Surface((self.rect.width + 12, self.rect.height + 12), pygame.SRCALPHA)
        body = pygame.Rect(6, 6, self.rect.width, self.rect.height)
        pygame.draw.rect(player_surface, MAGENTA, body, border_radius=8)
        pygame.draw.rect(player_surface, CYAN, body, width=3, border_radius=8)
        pygame.draw.circle(player_surface, WHITE, (body.left + 16, body.top + 16), 4)
        pygame.draw.circle(player_surface, WHITE, (body.left + 32, body.top + 16), 4)
        rotated = pygame.transform.rotate(player_surface, -self.rotation)
        draw_rect = rotated.get_rect(center=(self.rect.centerx - int(camera_x), self.rect.centery))
        surface.blit(rotated, draw_rect)
