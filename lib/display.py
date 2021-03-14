import os
import pygame

from .event_manager import EventManager

COLOR_DEFAULT_FOREGROUND = (255, 255, 255)
COLOR_DEFAULT_BACKGROUND = (0, 0, 0)
COLOR_DEFAULT_BORDER = COLOR_DEFAULT_BACKGROUND
COLOR_GHOST_TEXT = (25, 25, 25)


class Display:

    device = '/dev/fb1'
    videodriver = 'fbcon'
    rect = pygame.Rect(0, 0, 320, 240)

    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        os.putenv('SDL_FBDEV', self.device)
        os.putenv('SDL_VIDEODRIVER', self.videodriver)
        pygame.font.init()
        pygame.display.init()
        pygame.mouse.set_visible(False)
        self.bg_color = COLOR_DEFAULT_BACKGROUND
        self.surface = pygame.display.set_mode((self.rect.width, self.rect.height))

    @staticmethod
    def shut_down():
        pygame.display.quit()
        pygame.font.quit()

    def clear(self):
        self.surface.fill(self.bg_color)
        pygame.display.update()
