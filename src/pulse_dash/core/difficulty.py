from __future__ import annotations

from dataclasses import dataclass
import random

import pygame

from pulse_dash.core.config import CONFIG
from pulse_dash.entities.obstacle import Spike


@dataclass(frozen=True)
class DifficultySnapshot:
    """Runtime difficulty values derived from elapsed play time."""

    elapsed: float
    normalized: float
    spawn_interval: float
    gap_px: int
    group_size: int


class DifficultyCurve:
    """Time-based obstacle progression.

    The first seconds are intentionally forgiving. Afterwards, spike frequency
    increases smoothly by reducing the delay and distance between generated
    obstacle groups. The curve is deterministic and centralized here so it can
    be tuned without touching the game loop.
    """

    def __init__(self, ramp_seconds: float | None = None) -> None:
        self.ramp_seconds = ramp_seconds or CONFIG.difficulty_ramp_seconds

    def snapshot(self, elapsed: float) -> DifficultySnapshot:
        if elapsed < CONFIG.difficulty_warmup_seconds:
            normalized = 0.0
        else:
            normalized = min(1.0, (elapsed - CONFIG.difficulty_warmup_seconds) / self.ramp_seconds)

        # Smoothstep avoids abrupt changes when the game leaves the warmup.
        t = normalized * normalized * (3.0 - 2.0 * normalized)
        interval = CONFIG.obstacle_spawn_interval_start + (
            CONFIG.obstacle_spawn_interval_end - CONFIG.obstacle_spawn_interval_start
        ) * t
        gap = int(CONFIG.obstacle_gap_start + (CONFIG.obstacle_gap_end - CONFIG.obstacle_gap_start) * t)

        if normalized < 0.38:
            group_size = 1
        elif normalized < 0.72:
            group_size = 2
        else:
            group_size = 3

        return DifficultySnapshot(
            elapsed=elapsed,
            normalized=normalized,
            spawn_interval=interval,
            gap_px=gap,
            group_size=group_size,
        )


class ObstacleSpawner:
    """Procedurally adds ground spikes ahead of the player.

    Obstacles are spawned outside the right side of the viewport. Because the
    player has constant horizontal velocity, a time-based interval maps cleanly
    to perceived frequency without producing impossible jumps.
    """

    def __init__(self, *, seed: int = 42) -> None:
        self.curve = DifficultyCurve()
        self.random = random.Random(seed)
        self.next_spawn_time = CONFIG.difficulty_warmup_seconds
        self.last_spawn_x = 0

    def reset(self) -> None:
        self.next_spawn_time = CONFIG.difficulty_warmup_seconds
        self.last_spawn_x = 0
        self.random.seed(42)

    def update(self, elapsed: float, player_x: int, spikes: list[Spike]) -> DifficultySnapshot:
        snapshot = self.curve.snapshot(elapsed)
        if elapsed >= self.next_spawn_time:
            self._spawn_group(player_x, spikes, snapshot)
            jitter = self.random.uniform(-CONFIG.obstacle_spawn_jitter, CONFIG.obstacle_spawn_jitter)
            self.next_spawn_time = elapsed + max(CONFIG.obstacle_spawn_interval_end, snapshot.spawn_interval + jitter)
        self._discard_old_spikes(player_x, spikes)
        return snapshot

    def _spawn_group(self, player_x: int, spikes: list[Spike], snapshot: DifficultySnapshot) -> None:
        spawn_x = max(
            player_x + CONFIG.obstacle_spawn_ahead_px,
            self.last_spawn_x + snapshot.gap_px,
        )
        spawn_x += self.random.randint(-CONFIG.obstacle_horizontal_jitter_px, CONFIG.obstacle_horizontal_jitter_px)
        spawn_x = max(spawn_x, player_x + CONFIG.obstacle_min_safe_ahead_px)

        # Triple spike groups are reserved for late-game and are slightly more
        # spread out to keep the pattern demanding but still fair.
        local_spacing = 58 if snapshot.group_size < 3 else 64
        for index in range(snapshot.group_size):
            rect = pygame.Rect(
                int(spawn_x + index * local_spacing),
                CONFIG.ground_y - CONFIG.obstacle_size,
                CONFIG.obstacle_size,
                CONFIG.obstacle_size,
            )
            spikes.append(Spike(rect))

        self.last_spawn_x = int(spawn_x + (snapshot.group_size - 1) * local_spacing)

    @staticmethod
    def _discard_old_spikes(player_x: int, spikes: list[Spike]) -> None:
        cutoff = player_x - CONFIG.width
        spikes[:] = [spike for spike in spikes if spike.rect.right >= cutoff]
