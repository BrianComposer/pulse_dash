from __future__ import annotations

import math

import pygame

from pulse_dash.core.camera import Camera
from pulse_dash.core.colors import BG_BOTTOM, BG_TOP, CYAN, DARK, GREEN, MAGENTA, MUTED, RED, WHITE, YELLOW
from pulse_dash.core.config import CONFIG
from pulse_dash.core.input import InputState
from pulse_dash.core.particles import ParticleSystem
from pulse_dash.core.utils import clamp, draw_text, draw_vertical_gradient, rounded_panel
from pulse_dash.entities.player import Player
from pulse_dash.levels.level_loader import Level, load_level
from pulse_dash.states.base_state import BaseState


class PlayingState(BaseState):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.level: Level = load_level(CONFIG.level_name)
        self.player = Player.create(*self.level.spawn)
        self.camera = Camera()
        self.particles = ParticleSystem()
        self.time = 0.0
        self.score = 0
        self.coins = 0
        self.paused = False
        self.finished = False

    def handle_input(self, input_state: InputState) -> None:
        if input_state.quit_requested:
            self.game.running = False
            return
        if input_state.pause_pressed:
            self.paused = not self.paused
        if not self.paused:
            self.player.request_jump(pressed=input_state.jump_pressed, held=input_state.jump_held)
        if input_state.restart_pressed:
            self.game.change_state(PlayingState(self.game))

    def update(self, dt: float) -> None:
        if self.paused:
            return
        self.time += dt
        self.player.update(dt, self.level.platform_rects)
        if self.player.jumped_this_frame:
            self.particles.emit_burst(self.player.rect.left, self.player.rect.bottom, 8, CYAN)
        self.camera.update(self.player.rect, dt)
        self.particles.emit_trail(self.player.rect.left, self.player.rect.centery)
        self.particles.update(dt)

        for coin in self.level.coins:
            coin.update(dt)
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.coins += 1
                self.score += 250
                self.particles.emit_burst(coin.rect.centerx, coin.rect.centery, 20, YELLOW)

        for spike in self.level.spikes:
            if self.player.rect.colliderect(spike.rect.inflate(-14, -10)):
                self._die()
                return

        if not self.player.alive:
            self._die()
            return

        progress = self.progress_percent()
        self.score = max(self.score, int(progress * 10)) + self.coins * 250
        if self.player.rect.centerx >= self.level.length:
            self._finish()

    def _die(self) -> None:
        from pulse_dash.states.game_over import GameOverState

        self.camera.shake()
        self.particles.emit_burst(self.player.rect.centerx, self.player.rect.centery, 30, RED)
        self.game.change_state(GameOverState(self.game, False, self.score, self.coins, self.progress_percent()))

    def _finish(self) -> None:
        from pulse_dash.states.game_over import GameOverState

        self.game.change_state(GameOverState(self.game, True, self.score + 1000, self.coins, 100))

    def progress_percent(self) -> int:
        return int(clamp(self.player.rect.centerx / self.level.length, 0, 1) * 100)

    def draw(self, surface: pygame.Surface) -> None:
        draw_vertical_gradient(surface, BG_TOP, BG_BOTTOM)
        self._draw_background(surface)
        self._draw_finish_gate(surface)
        for platform in self.level.platforms:
            platform.draw(surface, self.camera.x)
        for spike in self.level.spikes:
            spike.draw(surface, self.camera.x)
        for coin in self.level.coins:
            coin.draw(surface, self.camera.x)
        self.particles.draw(surface, self.camera.x)
        self.player.draw(surface, self.camera.x)
        self._draw_hud(surface)
        if self.paused:
            self._draw_pause(surface)

    def _draw_background(self, surface: pygame.Surface) -> None:
        grid = CONFIG.background_grid_size
        offset = int(self.camera.x * 0.35) % grid
        for x in range(-offset, CONFIG.width + grid, grid):
            pygame.draw.line(surface, (20, 30, 58), (x, 0), (x, CONFIG.height), 1)
        for y in range(0, CONFIG.height, grid):
            pygame.draw.line(surface, (16, 22, 47), (0, y), (CONFIG.width, y), 1)
        for i in range(14):
            x = int((i * 310 - self.camera.x * 0.18) % (CONFIG.width + 200) - 100)
            y = int(90 + math.sin(self.time + i * 0.9) * 38 + (i % 5) * 58)
            radius = 2 + (i % 4)
            pygame.draw.circle(surface, CYAN if i % 2 else MAGENTA, (x, y), radius)

    def _draw_finish_gate(self, surface: pygame.Surface) -> None:
        x = int(self.level.length - self.camera.x)
        if -100 < x < CONFIG.width + 100:
            pygame.draw.rect(surface, GREEN, (x, 260, 16, 260), border_radius=8)
            pygame.draw.circle(surface, WHITE, (x + 8, 250), 18, width=3)
            draw_text(surface, "FIN", self.game.assets.font_small, GREEN, (x + 8, 225), shadow=False)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        progress = self.progress_percent()
        pygame.draw.rect(surface, DARK, (40, 28, 360, 22), border_radius=12)
        pygame.draw.rect(surface, CYAN, (40, 28, int(360 * progress / 100), 22), border_radius=12)
        pygame.draw.rect(surface, WHITE, (40, 28, 360, 22), width=2, border_radius=12)
        draw_text(surface, f"{progress}%", self.game.assets.font_small, WHITE, (430, 39), shadow=False)
        draw_text(surface, f"Score {self.score}", self.game.assets.font_small, WHITE, (1000, 34), shadow=False)
        draw_text(surface, f"Coins {self.coins}/{len(self.level.coins)}", self.game.assets.font_small, YELLOW, (1160, 34), shadow=False)

    def _draw_pause(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((CONFIG.width, CONFIG.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 135))
        surface.blit(overlay, (0, 0))
        rect = pygame.Rect(CONFIG.width // 2 - 220, CONFIG.height // 2 - 90, 440, 180)
        rounded_panel(surface, rect, (15, 19, 42), CYAN)
        draw_text(surface, "PAUSA", self.game.assets.font_large, WHITE, (CONFIG.width // 2, CONFIG.height // 2 - 25))
        draw_text(surface, "P/Esc para continuar · R reinicia", self.game.assets.font_medium, MUTED, (CONFIG.width // 2, CONFIG.height // 2 + 40))
