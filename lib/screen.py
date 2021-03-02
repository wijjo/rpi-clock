import os
import pygame
from .panel import Panel
from .utility import sub_rect


class Screen:

    device = '/dev/fb1'
    rect = pygame.Rect(0, 0, 320, 240)

    white = (255, 255, 255)
    black = (0, 0, 0)
    grey = (128, 128, 128)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

    font_size_medium = 50
    font_size_large = 100

    def __init__(self, bg_color=None):
        os.putenv('SDL_FBDEV', self.device)
        pygame.init()
        pygame.mouse.set_visible(False)
        self.bg_color = bg_color or self.black
        self.surface = pygame.display.set_mode((self.rect.width, self.rect.height))
        self.panel = Panel(self, self.rect)

    def clear(self):
        self.surface.fill(self.bg_color)
        pygame.display.update()
