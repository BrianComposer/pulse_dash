from __future__ import annotations

import math
from array import array
from dataclasses import dataclass, field
from typing import Literal

import pygame

from pulse_dash.core.config import CONFIG

WaveKind = Literal["square", "triangle", "noise"]


@dataclass
class AudioManager:
    """Small procedural chiptune audio engine.

    The game deliberately generates all sounds at runtime so the repository stays
    self-contained: no external WAV/OGG files are required. If SDL cannot open an
    audio device, the manager silently degrades to a no-op backend, which keeps
    headless tests and CI reliable.
    """

    enabled: bool = True
    sample_rate: int = 44100
    _sound_cache: dict[tuple, pygame.mixer.Sound] = field(default_factory=dict)
    _music_timer: float = 0.0
    _beat_timer: float = 0.0
    _step: int = 0
    _music_active: bool = False
    _lead_channel: pygame.mixer.Channel | None = None
    _bass_channel: pygame.mixer.Channel | None = None
    _sfx_channel: pygame.mixer.Channel | None = None
    _coin_channel: pygame.mixer.Channel | None = None

    def initialize(self) -> None:
        if not self.enabled:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1, buffer=512)
            pygame.mixer.set_num_channels(8)
            self._lead_channel = pygame.mixer.Channel(0)
            self._bass_channel = pygame.mixer.Channel(1)
            self._sfx_channel = pygame.mixer.Channel(2)
            self._coin_channel = pygame.mixer.Channel(3)
        except pygame.error:
            self.enabled = False

    def start_music(self) -> None:
        self._music_active = True

    def stop_music(self) -> None:
        self._music_active = False
        for channel in (self._lead_channel, self._bass_channel):
            if channel is not None:
                channel.stop()

    def update(self, dt: float, intensity: float = 0.0) -> None:
        if not self.enabled or not self._music_active:
            return
        intensity = max(0.0, min(1.0, intensity))
        bpm = CONFIG.music_bpm_start + (CONFIG.music_bpm_end - CONFIG.music_bpm_start) * intensity
        step_duration = 60.0 / bpm / 2.0  # eighth notes
        self._beat_timer += dt
        self._music_timer += dt
        while self._beat_timer >= step_duration:
            self._beat_timer -= step_duration
            self._play_music_step(intensity)
            self._step = (self._step + 1) % 32

    def play_jump(self) -> None:
        self._play_sfx(720, 0.065, CONFIG.sfx_volume, "square", slide_to=980)

    def play_coin(self) -> None:
        if not self.enabled or self._coin_channel is None:
            return
        try:
            self._coin_channel.play(self._tone(1568, 0.09, CONFIG.sfx_volume, "square"))
        except pygame.error:
            self.enabled = False

    def play_damage(self) -> None:
        self._play_sfx(210, 0.22, CONFIG.sfx_volume * 1.08, "noise", slide_to=80)

    def play_finish(self) -> None:
        self._play_sfx(880, 0.12, CONFIG.sfx_volume, "square")
        self._play_sfx(1320, 0.16, CONFIG.sfx_volume * 0.9, "triangle")

    def _play_music_step(self, intensity: float) -> None:
        if self._lead_channel is None or self._bass_channel is None:
            return

        lead_pattern = [659, 0, 784, 0, 988, 880, 784, 0, 659, 0, 784, 880, 988, 0, 1175, 0]
        counter_pattern = [0, 494, 0, 523, 0, 587, 0, 659, 0, 494, 0, 523, 587, 0, 659, 784]
        bass_pattern = [165, 165, 196, 196, 220, 220, 196, 196, 147, 147, 165, 165, 196, 196, 220, 220]

        idx = self._step % 16
        lead_freq = lead_pattern[idx]
        if intensity > 0.55 and self._step % 4 == 2:
            lead_freq = counter_pattern[idx] or lead_freq
        if lead_freq:
            snd = self._tone(lead_freq, 0.085, CONFIG.music_volume, "square")
            self._lead_channel.play(snd)

        if self._step % 2 == 0:
            bass_freq = bass_pattern[idx]
            snd = self._tone(bass_freq, 0.115, CONFIG.music_volume * 0.72, "triangle")
            self._bass_channel.play(snd)

    def _play_sfx(self, freq: float, duration: float, volume: float, wave: WaveKind, *, slide_to: float | None = None) -> None:
        if not self.enabled or self._sfx_channel is None:
            return
        try:
            self._sfx_channel.play(self._tone(freq, duration, volume, wave, slide_to=slide_to))
        except pygame.error:
            self.enabled = False

    def _tone(
        self,
        freq: float,
        duration: float,
        volume: float,
        wave: WaveKind = "square",
        *,
        slide_to: float | None = None,
    ) -> pygame.mixer.Sound:
        key = (round(freq, 3), round(duration, 3), round(volume, 3), wave, None if slide_to is None else round(slide_to, 3))
        cached = self._sound_cache.get(key)
        if cached is not None:
            return cached

        n_samples = max(1, int(self.sample_rate * duration))
        amplitude = int(32767 * max(0.0, min(1.0, volume)))
        data = array("h")
        phase = 0.0
        noise_seed = 0x12345

        for i in range(n_samples):
            t = i / max(1, n_samples - 1)
            current_freq = freq if slide_to is None else freq + (slide_to - freq) * t
            phase = (phase + current_freq / self.sample_rate) % 1.0
            envelope = min(1.0, i / max(1, int(self.sample_rate * 0.008))) * (1.0 - t) ** 1.7

            if wave == "square":
                value = 1.0 if phase < 0.5 else -1.0
            elif wave == "triangle":
                value = 4.0 * abs(phase - 0.5) - 1.0
            else:
                noise_seed = (1103515245 * noise_seed + 12345) & 0x7FFFFFFF
                value = ((noise_seed / 0x7FFFFFFF) * 2.0 - 1.0) * (1.0 - t * 0.35)

            data.append(int(amplitude * envelope * value))

        sound = pygame.mixer.Sound(buffer=data.tobytes())
        self._sound_cache[key] = sound
        return sound
