from __future__ import annotations

import math

import pygame

from pulse_dash.core.camera import Camera
from pulse_dash.core.colors import BG_BOTTOM, BG_TOP, CYAN, DARK, GREEN, MAGENTA, MUTED, RED, WHITE, YELLOW
from pulse_dash.core.config import CONFIG
from pulse_dash.core.difficulty import DifficultySnapshot, ObstacleSpawner
from pulse_dash.core.input import InputState
from pulse_dash.core.particles import ParticleSystem
from pulse_dash.core.stages import StageGenerator, StageSpec
from pulse_dash.core.utils import clamp, draw_text, draw_vertical_gradient, rounded_panel
from pulse_dash.entities.player import Player
from pulse_dash.levels.level_loader import Level
from pulse_dash.states.base_state import BaseState


class PlayingState(BaseState):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.stage_generator = StageGenerator()
        self.stage_index = 1
        self.stage_spec: StageSpec = self.stage_generator.spec_for(self.stage_index)
        self.level: Level = self.stage_generator.generate(self.stage_index)
        self.player = Player.create(*self.level.spawn)
        self.camera = Camera()
        self.particles = ParticleSystem()
        self.stage_time = 0.0
        self.total_time = 0.0
        self.score = 0
        self.coins = 0
        self.stage_coins = 0
        self.lives = CONFIG.start_lives
        self.paused = False
        self.stage_transition_timer = CONFIG.stage_transition_seconds
        self.obstacle_spawner = ObstacleSpawner(stage_index=self.stage_index)
        self.difficulty: DifficultySnapshot = self.obstacle_spawner.curve.snapshot(0.0)

    def enter(self) -> None:
        self.game.audio.start_music()

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
        self.stage_time += dt
        self.total_time += dt
        self.stage_transition_timer = max(0.0, self.stage_transition_timer - dt)
        self.player.update(dt, self.level.platform_rects)
        if self.player.jumped_this_frame:
            self.game.audio.play_jump()
            self.particles.emit_burst(self.player.rect.left, self.player.rect.bottom, 8, CYAN)
        self.camera.update(self.player.rect, dt)
        self.difficulty = self.obstacle_spawner.update(self.stage_time, self.player.rect.centerx, self.level.spikes)
        self.game.audio.update(dt, self.difficulty.normalized)
        self.particles.emit_trail(self.player.rect.left, self.player.rect.centery)
        self.particles.update(dt)

        for coin in self.level.coins:
            coin.update(dt)
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.coins += 1
                self.stage_coins += 1
                self.score += 250
                self.game.audio.play_coin()
                self.particles.emit_burst(coin.rect.centerx, coin.rect.centery, 20, YELLOW)

        for spike in self.level.spikes:
            if self.player.rect.colliderect(spike.rect.inflate(-14, -10)):
                self._take_damage()
                return

        if not self.player.alive:
            self._take_damage(reset_position=True)
            return

        progress = self.progress_percent()
        stage_bonus = (self.stage_index - 1) * 800
        self.score = max(self.score, int(progress * 10) + stage_bonus + self.coins * 250)
        if self.player.rect.centerx >= self.level.length:
            self._advance_stage()

    def _take_damage(self, *, reset_position: bool = False) -> None:
        if reset_position:
            self.player.alive = True
            self.player.rect.y = CONFIG.ground_y - self.player.rect.height
            self.player.velocity.y = 0
            damaged = True
            self.player.invulnerability_timer = CONFIG.damage_invulnerability_time
        else:
            damaged = self.player.take_damage()
        if not damaged:
            return

        self.lives -= 1
        self.camera.shake()
        self.game.audio.play_damage()
        self.particles.emit_burst(self.player.rect.centerx, self.player.rect.centery, 30, RED)

        if self.lives <= 0:
            self._die()

    def _die(self) -> None:
        from pulse_dash.states.game_over import GameOverState

        self.game.audio.stop_music()
        self.game.change_state(
            GameOverState(
                self.game,
                False,
                self.score,
                self.coins,
                self.progress_percent(),
                stage=self.stage_index,
                total_time=self.total_time,
            )
        )

    def _advance_stage(self) -> None:
        self.game.audio.play_finish()
        self.score += 1000 + self.stage_index * 350
        self.stage_index += 1
        self.stage_spec = self.stage_generator.spec_for(self.stage_index)
        self.level = self.stage_generator.generate(self.stage_index)
        self.player = Player.create(*self.level.spawn)
        self.camera = Camera()
        self.particles = ParticleSystem()
        self.stage_time = 0.0
        self.stage_coins = 0
        self.stage_transition_timer = CONFIG.stage_transition_seconds
        self.obstacle_spawner = ObstacleSpawner(stage_index=self.stage_index)
        self.difficulty = self.obstacle_spawner.curve.snapshot(0.0)

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
        if self.stage_transition_timer > 0.0:
            self._draw_stage_intro(surface)
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
            y = int(90 + math.sin(self.total_time + i * 0.9) * 38 + (i % 5) * 58)
            radius = 2 + (i % 4)
            pygame.draw.circle(surface, CYAN if i % 2 else MAGENTA, (x, y), radius)

    def _draw_finish_gate(self, surface: pygame.Surface) -> None:
        x = int(self.level.length - self.camera.x)
        if -100 < x < CONFIG.width + 100:
            pygame.draw.rect(surface, GREEN, (x, 260, 16, 260), border_radius=8)
            pygame.draw.circle(surface, WHITE, (x + 8, 250), 18, width=3)
            draw_text(surface, "NEXT", self.game.assets.font_small, GREEN, (x + 8, 225), shadow=False)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        progress = self.progress_percent()
        pygame.draw.rect(surface, DARK, (40, 28, 360, 22), border_radius=12)
        pygame.draw.rect(surface, CYAN, (40, 28, int(360 * progress / 100), 22), border_radius=12)
        pygame.draw.rect(surface, WHITE, (40, 28, 360, 22), width=2, border_radius=12)
        draw_text(surface, f"{progress}%", self.game.assets.font_small, WHITE, (430, 39), shadow=False)
        draw_text(surface, f"Stage {self.stage_index}", self.game.assets.font_small, GREEN, (545, 34), shadow=False)
        draw_text(surface, f"Score {self.score}", self.game.assets.font_small, WHITE, (1000, 34), shadow=False)
        draw_text(surface, f"Coins {self.coins} (+{self.stage_coins}/{len(self.level.coins)})", self.game.assets.font_small, YELLOW, (1130, 34), shadow=False)
        self._draw_lives(surface)
        intensity = int(self.difficulty.normalized * 100)
        draw_text(surface, f"Dificultad {intensity}%", self.game.assets.font_small, MUTED, (700, 34), shadow=False)

    def _draw_lives(self, surface: pygame.Surface) -> None:
        x = 520
        y = 58
        draw_text(surface, "Vidas", self.game.assets.font_small, WHITE, (x - 32, y + 11), shadow=False)
        for i in range(CONFIG.start_lives):
            rect = pygame.Rect(x + i * 24, y + 2, 18, 18)
            color = RED if i < self.lives else DARK
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, WHITE, rect, width=1, border_radius=5)

    def _draw_stage_intro(self, surface: pygame.Surface) -> None:
        alpha = int(220 * clamp(self.stage_transition_timer / CONFIG.stage_transition_seconds, 0, 1))
        overlay = pygame.Surface((CONFIG.width, CONFIG.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(120, alpha)))
        surface.blit(overlay, (0, 0))
        draw_text(surface, f"STAGE {self.stage_index}", self.game.assets.font_large, GREEN, (CONFIG.width // 2, 205))
        draw_text(
            surface,
            "más velocidad psicológica: pinchos más frecuentes y menos margen",
            self.game.assets.font_medium,
            CYAN,
            (CONFIG.width // 2, 265),
        )

    def _draw_pause(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((CONFIG.width, CONFIG.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 135))
        surface.blit(overlay, (0, 0))
        rect = pygame.Rect(CONFIG.width // 2 - 220, CONFIG.height // 2 - 90, 440, 180)
        rounded_panel(surface, rect, (15, 19, 42), CYAN)
        draw_text(surface, "PAUSA", self.game.assets.font_large, WHITE, (CONFIG.width // 2, CONFIG.height // 2 - 25))
        draw_text(surface, "P/Esc para continuar · R reinicia", self.game.assets.font_medium, MUTED, (CONFIG.width // 2, CONFIG.height // 2 + 40))
