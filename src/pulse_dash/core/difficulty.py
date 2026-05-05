from __future__ import annotations

from dataclasses import dataclass
import random

import pygame

from pulse_dash.core.config import CONFIG
from pulse_dash.entities.obstacle import Spike


@dataclass(frozen=True)
class DifficultySnapshot:
    """Runtime difficulty values derived from elapsed play time and stage index."""

    elapsed: float
    normalized: float
    spawn_interval: float
    gap_px: int
    group_size: int
    stage_index: int = 1


class DifficultyCurve:
    """Time and stage-based obstacle progression.

    Inside a stage, the first seconds are forgiving and the curve ramps smoothly.
    Across stages, a bounded difficulty bonus shifts the curve forward so each
    newly generated stage is slightly harder than the previous one.
    """

    def __init__(self, ramp_seconds: float | None = None, stage_index: int = 1) -> None:
        self.ramp_seconds = ramp_seconds or CONFIG.difficulty_ramp_seconds
        self.stage_index = max(1, stage_index)
        self.stage_bonus = min(CONFIG.stage_max_difficulty_bonus, (self.stage_index - 1) * CONFIG.stage_difficulty_step)

    def snapshot(self, elapsed: float) -> DifficultySnapshot:
        if elapsed < CONFIG.difficulty_warmup_seconds:
            temporal = 0.0
        else:
            temporal = min(1.0, (elapsed - CONFIG.difficulty_warmup_seconds) / self.ramp_seconds)

        normalized = min(1.0, temporal + self.stage_bonus)
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
            stage_index=self.stage_index,
        )


class ObstacleSpawner:
    """Procedurally adds ground spikes ahead of the player."""

    def __init__(self, *, seed: int = 42, stage_index: int = 1) -> None:
        self.stage_index = max(1, stage_index)
        self.curve = DifficultyCurve(stage_index=self.stage_index)
        self.base_seed = seed
        self.random = random.Random(seed + self.stage_index * 4099)
        self.next_spawn_time = CONFIG.difficulty_warmup_seconds
        self.last_spawn_x = 0

    def reset(self) -> None:
        self.next_spawn_time = CONFIG.difficulty_warmup_seconds
        self.last_spawn_x = 0
        self.random.seed(self.base_seed + self.stage_index * 4099)

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
