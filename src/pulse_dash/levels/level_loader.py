from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources

import pygame

from pulse_dash.entities.coin import Coin
from pulse_dash.entities.obstacle import Spike
from pulse_dash.entities.platform import Platform


@dataclass
class Level:
    name: str
    length: int
    spawn: tuple[int, int]
    platforms: list[Platform]
    spikes: list[Spike]
    coins: list[Coin]

    @property
    def platform_rects(self) -> list[pygame.Rect]:
        return [platform.rect for platform in self.platforms]


def _rect_from_data(data: dict[str, int]) -> pygame.Rect:
    return pygame.Rect(data["x"], data["y"], data["w"], data["h"])


def load_level(filename: str) -> Level:
    with resources.files("pulse_dash.levels").joinpath(filename).open("r", encoding="utf-8") as file:
        data = json.load(file)

    return Level(
        name=data.get("name", "Untitled Level"),
        length=int(data["length"]),
        spawn=(int(data["spawn"]["x"]), int(data["spawn"]["y"])),
        platforms=[Platform(_rect_from_data(item)) for item in data.get("platforms", [])],
        spikes=[Spike(_rect_from_data(item)) for item in data.get("spikes", [])],
        coins=[Coin(_rect_from_data(item)) for item in data.get("coins", [])],
    )
