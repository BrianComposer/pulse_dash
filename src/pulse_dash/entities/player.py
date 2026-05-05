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
    jump_buffer_timer: float = 0.0
    coyote_timer: float = 0.0
    jumped_this_frame: bool = False
    invulnerability_timer: float = 0.0

    @classmethod
    def create(cls, x: int = 120, y: int | None = None) -> "Player":
        size = 48
        initial_y = y if y is not None else CONFIG.ground_y - size
        return cls(rect=pygame.Rect(x, initial_y, size, size), velocity=pygame.Vector2(CONFIG.player_speed, 0))

    def request_jump(self, *, pressed: bool, held: bool = False) -> None:
        """Queue a jump request so near-ground inputs are not lost.

        `pressed` stores a real jump buffer. `held` keeps a short rolling buffer so
        holding SPACE produces the expected auto-jump on landing without relying on
        OS-level key repeat.
        """
        if pressed:
            self.jump_buffer_timer = CONFIG.jump_buffer_time
        elif held:
            self.jump_buffer_timer = max(self.jump_buffer_timer, CONFIG.hold_jump_buffer_time)

    def jump(self) -> None:
        """Backward-compatible immediate jump used by tests or external callers."""
        self.request_jump(pressed=True, held=False)
        if self.on_ground and self.alive:
            self._perform_jump()

    def _perform_jump(self) -> None:
        self.velocity.y = CONFIG.jump_velocity
        self.on_ground = False
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.jumped_this_frame = True

    def _can_jump(self) -> bool:
        return self.on_ground or self.coyote_timer > 0.0

    def is_invulnerable(self) -> bool:
        return self.invulnerability_timer > 0.0

    def take_damage(self) -> bool:
        """Return True only when a hit actually consumes a life."""
        if self.is_invulnerable() or not self.alive:
            return False
        self.invulnerability_timer = CONFIG.damage_invulnerability_time
        self.velocity.y = CONFIG.damage_bounce_velocity
        return True

    def update(self, dt: float, platforms: list[pygame.Rect]) -> None:
        if not self.alive:
            return

        self.jumped_this_frame = False
        dt = min(dt, 1 / 20)
        if self.invulnerability_timer > 0.0:
            self.invulnerability_timer = max(0.0, self.invulnerability_timer - dt)

        if self.on_ground:
            self.coyote_timer = CONFIG.coyote_time
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)

        if self.jump_buffer_timer > 0.0 and self._can_jump():
            self._perform_jump()

        self.velocity.x = CONFIG.player_speed
        self.velocity.y = min(self.velocity.y + CONFIG.gravity * dt, CONFIG.max_fall_speed)

        previous_bottom = self.rect.bottom
        self.rect.x += round(self.velocity.x * dt)
        self.rect.y += round(self.velocity.y * dt)
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform) and self.velocity.y >= 0:
                if previous_bottom <= platform.top + 10:
                    self.rect.bottom = platform.top
                    self.velocity.y = 0
                    self.on_ground = True
                    self.coyote_timer = CONFIG.coyote_time
                    break

        # If SPACE was pressed just before landing, consume the buffered jump as soon
        # as the landing is detected. The upward motion begins on the next frame, but
        # the input never disappears.
        if self.jump_buffer_timer > 0.0 and self.on_ground:
            self._perform_jump()

        if self.jump_buffer_timer > 0.0:
            self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - dt)

        if self.rect.top > CONFIG.height + 160:
            self.alive = False

        if not self.on_ground:
            self.rotation = (self.rotation + 420 * dt) % 360
        else:
            self.rotation = round(self.rotation / 90) * 90

    def draw(self, surface: pygame.Surface, camera_x: float) -> None:
        if self.is_invulnerable() and int(self.invulnerability_timer * 18) % 2 == 0:
            return
        player_surface = pygame.Surface((self.rect.width + 12, self.rect.height + 12), pygame.SRCALPHA)
        body = pygame.Rect(6, 6, self.rect.width, self.rect.height)
        pygame.draw.rect(player_surface, MAGENTA, body, border_radius=8)
        pygame.draw.rect(player_surface, CYAN, body, width=3, border_radius=8)
        pygame.draw.circle(player_surface, WHITE, (body.left + 16, body.top + 16), 4)
        pygame.draw.circle(player_surface, WHITE, (body.left + 32, body.top + 16), 4)
        rotated = pygame.transform.rotate(player_surface, -self.rotation)
        draw_rect = rotated.get_rect(center=(self.rect.centerx - int(camera_x), self.rect.centery))
        surface.blit(rotated, draw_rect)
