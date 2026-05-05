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
    ground_y: int = 520
    level_name: str = "level_01.json"
    camera_dead_zone_x: int = 360
    background_grid_size: int = 64
    start_lives: int = 1


CONFIG = GameConfig()
