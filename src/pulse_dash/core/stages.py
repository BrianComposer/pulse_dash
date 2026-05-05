from __future__ import annotations

from dataclasses import dataclass
import random

import pygame

from pulse_dash.core.config import CONFIG
from pulse_dash.entities.coin import Coin
from pulse_dash.entities.platform import Platform
from pulse_dash.levels.level_loader import Level


@dataclass(frozen=True)
class StageSpec:
    """Immutable parameters for one procedurally generated stage."""

    index: int
    name: str
    length: int
    difficulty_bonus: float
    coin_count: int
    platform_count: int


class StageGenerator:
    """Builds an endless sequence of deterministic procedural stages.

    Stage 1 is deliberately gentle. Each subsequent stage is longer and gives
    the obstacle spawner a higher difficulty bonus. The generator is seeded with
    the stage index, so a given stage number always has stable geometry while
    the overall run remains infinite.
    """

    def __init__(self, *, seed: int = 1337) -> None:
        self.seed = seed

    def spec_for(self, index: int) -> StageSpec:
        safe_index = max(1, index)
        difficulty_bonus = min(CONFIG.stage_max_difficulty_bonus, (safe_index - 1) * CONFIG.stage_difficulty_step)
        length = min(
            CONFIG.stage_max_length,
            CONFIG.stage_base_length + (safe_index - 1) * CONFIG.stage_length_growth,
        )
        coin_count = min(CONFIG.stage_max_coins, CONFIG.stage_base_coins + safe_index // 2)
        platform_count = min(CONFIG.stage_max_extra_platforms, CONFIG.stage_base_extra_platforms + safe_index // 3)
        return StageSpec(
            index=safe_index,
            name=f"Stage {safe_index:02d}",
            length=length,
            difficulty_bonus=difficulty_bonus,
            coin_count=coin_count,
            platform_count=platform_count,
        )

    def generate(self, index: int) -> Level:
        spec = self.spec_for(index)
        rng = random.Random(self.seed + spec.index * 9973)
        platforms = [
            Platform(
                pygame.Rect(
                    0,
                    CONFIG.ground_y,
                    spec.length + CONFIG.width * 2,
                    CONFIG.ground_height,
                )
            )
        ]

        # Optional aerial platforms are mainly for coins; they do not create
        # mandatory precision jumps, so the stage remains fair even late-game.
        usable_start = 1100
        usable_end = max(usable_start + 1, spec.length - 1700)
        for i in range(spec.platform_count):
            x = int(usable_start + (i + 1) * (usable_end - usable_start) / (spec.platform_count + 1))
            x += rng.randint(-220, 220)
            y = rng.choice([390, 405, 420, 435]) - min(28, spec.index * 2)
            w = rng.randint(175, 280)
            platforms.append(Platform(pygame.Rect(x, y, w, 26)))

        coins: list[Coin] = []
        for i in range(spec.coin_count):
            x = int(760 + i * (spec.length - 1520) / max(1, spec.coin_count - 1))
            x += rng.randint(-160, 160)
            on_upper = i % 3 == 1 and len(platforms) > 1
            if on_upper:
                platform = platforms[1 + (i % (len(platforms) - 1))]
                x = platform.rect.centerx + rng.randint(-45, 45)
                y = platform.rect.top - 50
            else:
                y = CONFIG.ground_y - 90 - rng.randint(0, 35)
            coins.append(Coin(pygame.Rect(x, y, 34, 34)))

        return Level(
            name=spec.name,
            length=spec.length,
            spawn=(CONFIG.stage_spawn_x, CONFIG.ground_y - CONFIG.player_size),
            platforms=platforms,
            spikes=[],
            coins=coins,
        )
