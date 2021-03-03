import os
import pygame

from .events import EventManager
from .typing import Color, FontSize

WHITE: Color = (255, 255, 255)
BLACK: Color = (0, 0, 0)
GREY: Color = (128, 128, 128)
RED: Color = (255, 0, 0)
GREEN: Color = (0, 255, 0)
BLUE: Color = (0, 0, 255)

COLOR_DEFAULT_TEXT = WHITE
COLOR_DEFAULT_BACKGROUND = BLACK

FONT_SIZE_MEDIUM: FontSize = 50
FONT_SIZE_LARGE: FontSize = 100
FONT_SIZE_DEFAULT = 25


class Display:

    device = '/dev/fb1'
    rect = pygame.Rect(0, 0, 320, 240)

    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        os.putenv('SDL_FBDEV', self.device)
        pygame.init()
        pygame.mouse.set_visible(False)
        self.bg_color = BLACK
        self.surface = pygame.display.set_mode((self.rect.width, self.rect.height))

    def clear(self):
        self.surface.fill(self.bg_color)
        pygame.display.update()
