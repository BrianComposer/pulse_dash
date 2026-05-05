from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GameConfig:
    title: str = "Pulse Dash"
    width: int = 1280
    height: int = 720
    fps: int = 60
    gravity: float = 2450.0
    jump_velocity: float = -880.0
    jump_buffer_time: float = 0.14
    hold_jump_buffer_time: float = 0.05
    coyote_time: float = 0.08
    max_fall_speed: float = 1450.0
    player_speed: float = 435.0
    player_size: int = 48
    ground_y: int = 520
    ground_height: int = 46
    level_name: str = "level_01.json"
    camera_dead_zone_x: int = 360
    background_grid_size: int = 64
    start_lives: int = 3
    damage_invulnerability_time: float = 1.15
    damage_bounce_velocity: float = -520.0
    damage_knockback_speed: float = 360.0
    music_volume: float = 0.18
    sfx_volume: float = 0.42
    music_bpm_start: float = 132.0
    music_bpm_end: float = 166.0

    # Time-based procedural difficulty. The game starts almost as a tutorial
    # and progressively increases obstacle frequency.
    difficulty_warmup_seconds: float = 3.2
    difficulty_ramp_seconds: float = 42.0
    obstacle_size: int = 46
    obstacle_spawn_ahead_px: int = 1040
    obstacle_min_safe_ahead_px: int = 840
    obstacle_spawn_interval_start: float = 2.35
    obstacle_spawn_interval_end: float = 0.72
    obstacle_spawn_jitter: float = 0.18
    obstacle_gap_start: int = 760
    obstacle_gap_end: int = 305
    obstacle_horizontal_jitter_px: int = 42

    # Endless stage system. Each cleared stage is generated procedurally and
    # increases the obstacle curve without creating an abrupt difficulty wall.
    stage_spawn_x: int = 120
    stage_base_length: int = 7200
    stage_length_growth: int = 850
    stage_max_length: int = 14500
    stage_transition_seconds: float = 1.35
    stage_difficulty_step: float = 0.115
    stage_max_difficulty_bonus: float = 0.78
    stage_base_coins: int = 5
    stage_max_coins: int = 12
    stage_base_extra_platforms: int = 2
    stage_max_extra_platforms: int = 6


CONFIG = GameConfig()
