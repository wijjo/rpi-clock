import pygame
from typing import Union

from .utility import sub_rect


class Panel:

    def __init__(self, display, rect):
        self.display = display
        self.rect = rect
        self.font_size = self.rect.height
        self.fx = 0
        self.fy = 0
        self.color = self.display.white
        self.bg_color = self.display.black
        self._font = None

    def configure(self,
                  fx=None,
                  fy=None,
                  font_size=None,
                  color=None,
                  bg_color=None):
        if fx is not None:
            self.fx = fx
        if fy is not None:
            self.fy = fy
        if font_size is not None:
            self.font_size = font_size
        if color is not None:
            self.color = color
        if bg_color is not None:
            self.bg_color = bg_color

    @property
    def font(self):
        if self._font is None:
            self._font = pygame.font.Font(None, self.font_size)
        return self._font

    def clear(self):
        self.display.surface.fill(self.bg_color, rect=self.rect)

    def text(self, text, duration: Union[int, float] = None):
        self.clear()
        text_width, text_height = self.font.size(text)
        text_rect = sub_rect(self.rect,
                             fleft=self.fx,
                             ftop=self.fy,
                             width=text_width,
                             height=text_height)
        text_surface = self.font.render(text, True, self.color)
        self.display.surface.blit(text_surface, text_rect)
        pygame.display.update()
        if duration is not None:
            self.display.event_manager.register('timer', self.clear, duration, max_count=1)

    def hsplit(self, x=None, fx=None):
        if fx is None:
            if x is None:
                left_width = self.rect.width / 2
            else:
                left_width = x
        else:
            left_width = int(fx * self.rect.width)
        right_width = self.rect.width - left_width
        left_rect = pygame.Rect(self.rect.left, self.rect.top, left_width, self.rect.height)
        right_rect = pygame.Rect(left_rect.right, self.rect.top, right_width, self.rect.height)
        return self.__class__(self.display, left_rect), self.__class__(self.display, right_rect)

    def vsplit(self, y=None, fy=None):
        if fy is None:
            if y is None:
                above_height = self.rect.height / 2
            else:
                above_height = y
        else:
            above_height = int(fy * self.rect.height)
        below_height = self.rect.height - above_height
        above_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect.width, above_height)
        below_rect = pygame.Rect(self.rect.left, above_rect.bottom, self.rect.width, below_height)
        return self.__class__(self.display, above_rect), self.__class__(self.display, below_rect)

    def __str__(self):
        return 'Panel(rect={}, fx={}, fy={}, color={}, bg_color={})'.format(
                    self.rect, self.fx, self.fy, self.color, self.bg_color)
