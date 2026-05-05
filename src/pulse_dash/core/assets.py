from __future__ import annotations

from dataclasses import dataclass

import pygame

from pulse_dash.core.colors import CYAN, DARK, GREEN, MAGENTA, ORANGE, PLATFORM, PURPLE, RED, WHITE, YELLOW


@dataclass
class AssetStore:
    font_title: pygame.font.Font
    font_large: pygame.font.Font
    font_medium: pygame.font.Font
    font_small: pygame.font.Font
    player: pygame.Surface
    spike: pygame.Surface
    coin_frames: list[pygame.Surface]
    platform_tile: pygame.Surface


def _make_player() -> pygame.Surface:
    surf = pygame.Surface((52, 52), pygame.SRCALPHA)
    pygame.draw.rect(surf, MAGENTA, (4, 4, 44, 44), border_radius=8)
    pygame.draw.rect(surf, CYAN, (4, 4, 44, 44), width=3, border_radius=8)
    pygame.draw.circle(surf, WHITE, (20, 20), 5)
    pygame.draw.circle(surf, WHITE, (34, 20), 5)
    pygame.draw.rect(surf, DARK, (18, 34, 18, 4), border_radius=2)
    return surf


def _make_spike() -> pygame.Surface:
    surf = pygame.Surface((52, 52), pygame.SRCALPHA)
    points = [(26, 2), (50, 50), (2, 50)]
    pygame.draw.polygon(surf, RED, points)
    pygame.draw.polygon(surf, ORANGE, [(26, 8), (43, 47), (9, 47)], width=3)
    pygame.draw.line(surf, WHITE, (26, 10), (26, 33), 2)
    return surf


def _make_coin_frames() -> list[pygame.Surface]:
    frames: list[pygame.Surface] = []
    for i in range(8):
        surf = pygame.Surface((42, 42), pygame.SRCALPHA)
        width = max(7, int(28 * abs(__import__("math").cos(i / 8 * 3.14159))))
        rect = pygame.Rect(21 - width // 2, 7, width, 28)
        pygame.draw.ellipse(surf, YELLOW, rect)
        pygame.draw.ellipse(surf, WHITE, rect, width=2)
        pygame.draw.line(surf, ORANGE, (21, 12), (21, 30), 2)
        frames.append(surf)
    return frames


def _make_platform_tile() -> pygame.Surface:
    surf = pygame.Surface((64, 32), pygame.SRCALPHA)
    pygame.draw.rect(surf, PLATFORM, (0, 0, 64, 32), border_radius=6)
    pygame.draw.rect(surf, CYAN, (0, 0, 64, 32), width=2, border_radius=6)
    pygame.draw.line(surf, PURPLE, (5, 26), (59, 26), 2)
    return surf


def load_assets() -> AssetStore:
    pygame.font.init()
    return AssetStore(
        font_title=pygame.font.Font(None, 96),
        font_large=pygame.font.Font(None, 56),
        font_medium=pygame.font.Font(None, 36),
        font_small=pygame.font.Font(None, 24),
        player=_make_player(),
        spike=_make_spike(),
        coin_frames=_make_coin_frames(),
        platform_tile=_make_platform_tile(),
    )
