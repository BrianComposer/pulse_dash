from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable

import pygame


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    center: tuple[int, int],
    shadow: bool = True,
) -> None:
    if shadow:
        shadow_img = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_img.get_rect(center=(center[0] + 3, center[1] + 4))
        surface.blit(shadow_img, shadow_rect)
    image = font.render(text, True, color)
    rect = image.get_rect(center=center)
    surface.blit(image, rect)


def draw_vertical_gradient(surface: pygame.Surface, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> None:
    height = surface.get_height()
    width = surface.get_width()
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(lerp(top[i], bottom[i], t)) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (width, y))


def rounded_panel(surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int], border: tuple[int, int, int] | None = None) -> None:
    pygame.draw.rect(surface, color, rect, border_radius=18)
    if border:
        pygame.draw.rect(surface, border, rect, width=2, border_radius=18)


def pulse(t: float, speed: float = 2.5, amount: float = 0.5) -> float:
    return 1.0 + math.sin(t * speed) * amount


def rects_from_objects(objects: Iterable[object]) -> list[pygame.Rect]:
    return [obj.rect for obj in objects if hasattr(obj, "rect")]
