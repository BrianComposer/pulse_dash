from __future__ import annotations

import os

import pygame

from pulse_dash.core.assets import AssetStore, load_assets
from pulse_dash.core.config import CONFIG
from pulse_dash.core.input import InputState
from pulse_dash.states.base_state import BaseState
from pulse_dash.states.menu import MenuState


class Game:
    def __init__(self, headless: bool = False) -> None:
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        pygame.init()
        pygame.display.set_caption(CONFIG.title)
        self.screen = pygame.display.set_mode((CONFIG.width, CONFIG.height))
        self.clock = pygame.time.Clock()
        self.assets: AssetStore = load_assets()
        self.running = True
        self.state: BaseState = MenuState(self)
        self.state.enter()

    def change_state(self, state: BaseState) -> None:
        self.state = state
        self.state.enter()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(CONFIG.fps) / 1000.0
            self.step(dt)
        pygame.quit()

    def step(self, dt: float) -> None:
        events = pygame.event.get()
        input_state = InputState.from_events(events)
        if input_state.quit_requested:
            self.running = False
            return
        self.state.handle_input(input_state)
        self.state.update(min(dt, 1 / 20))
        self.state.draw(self.screen)
        pygame.display.flip()
