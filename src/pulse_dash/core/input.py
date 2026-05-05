from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class InputState:
    jump_pressed: bool = False
    confirm_pressed: bool = False
    pause_pressed: bool = False
    restart_pressed: bool = False
    quit_requested: bool = False

    @classmethod
    def from_events(cls, events: list[pygame.event.Event]) -> "InputState":
        state = cls()
        for event in events:
            if event.type == pygame.QUIT:
                state.quit_requested = True
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    state.jump_pressed = True
                    state.confirm_pressed = True
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    state.confirm_pressed = True
                elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                    state.pause_pressed = True
                elif event.key == pygame.K_r:
                    state.restart_pressed = True
        return state
