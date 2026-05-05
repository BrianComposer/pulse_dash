from __future__ import annotations

from dataclasses import dataclass, field
import random

import pygame

from pulse_dash.core.colors import CYAN, MAGENTA, YELLOW


@dataclass
class Particle:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: float
    color: tuple[int, int, int]
    lifetime: float
    age: float = 0.0

    def update(self, dt: float) -> bool:
        self.age += dt
        self.pos += self.vel * dt
        self.vel *= 0.985
        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface, camera_x: float) -> None:
        alpha = max(0, 255 - int(255 * self.age / self.lifetime))
        r = max(1, int(self.radius * (1 - self.age / self.lifetime)))
        temp = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(temp, (*self.color, alpha), (r * 2, r * 2), r)
        surface.blit(temp, (int(self.pos.x - camera_x - r * 2), int(self.pos.y - r * 2)))


@dataclass
class ParticleSystem:
    particles: list[Particle] = field(default_factory=list)

    def emit_burst(self, x: float, y: float, count: int = 18, color: tuple[int, int, int] | None = None) -> None:
        palette = [CYAN, MAGENTA, YELLOW]
        for _ in range(count):
            angle = random.uniform(-3.14, 3.14)
            speed = random.uniform(80, 380)
            vel = pygame.Vector2(speed, 0).rotate_rad(angle)
            self.particles.append(
                Particle(
                    pos=pygame.Vector2(x, y),
                    vel=vel,
                    radius=random.uniform(3, 8),
                    color=color or random.choice(palette),
                    lifetime=random.uniform(0.35, 0.85),
                )
            )

    def emit_trail(self, x: float, y: float) -> None:
        if random.random() < 0.65:
            self.particles.append(
                Particle(
                    pos=pygame.Vector2(x, y),
                    vel=pygame.Vector2(random.uniform(-130, -40), random.uniform(-40, 40)),
                    radius=random.uniform(2, 5),
                    color=random.choice([CYAN, MAGENTA]),
                    lifetime=random.uniform(0.25, 0.55),
                )
            )

    def update(self, dt: float) -> None:
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface: pygame.Surface, camera_x: float) -> None:
        for particle in self.particles:
            particle.draw(surface, camera_x)
