from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pulse_dash.core.difficulty import DifficultyCurve, ObstacleSpawner  # noqa: E402
from pulse_dash.core.config import CONFIG  # noqa: E402


def main() -> None:
    curve = DifficultyCurve()
    early = curve.snapshot(0.5)
    middle = curve.snapshot(CONFIG.difficulty_warmup_seconds + CONFIG.difficulty_ramp_seconds * 0.55)
    late = curve.snapshot(CONFIG.difficulty_warmup_seconds + CONFIG.difficulty_ramp_seconds + 4.0)

    assert early.spawn_interval > middle.spawn_interval > late.spawn_interval
    assert early.gap_px > middle.gap_px > late.gap_px
    assert early.group_size == 1
    assert middle.group_size >= 2
    assert late.group_size == 3

    spikes = []
    spawner = ObstacleSpawner(seed=7)
    snapshot = spawner.update(CONFIG.difficulty_warmup_seconds + 0.1, 120, spikes)
    assert snapshot.normalized >= 0.0
    assert len(spikes) == 1
    assert spikes[0].rect.left >= 120 + CONFIG.obstacle_min_safe_ahead_px

    print("difficulty_curve_test: OK")


if __name__ == "__main__":
    main()
