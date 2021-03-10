import pygame
from typing import Optional, List

from . import log
from .display import Display, COLOR_DEFAULT_FOREGROUND, COLOR_DEFAULT_BACKGROUND
from .typing import Color, FontSize, Position, Rect, Interval
from .utility import sub_rect


# noinspection DuplicatedCode
class Viewport:

    def __init__(self, display: Display, rect: Optional[Rect]):
        """
        Construct viewport.

        :param display: display for text, image, etc.
        :param rect: rectangle to frame displayed object (None for "null" viewport)
        """
        self.display = display
        self.rect = rect
        self.font_size = self.rect.height
        self.fx = 0
        self.fy = 0
        self.color = COLOR_DEFAULT_FOREGROUND
        self.bg_color = COLOR_DEFAULT_BACKGROUND
        self._font = None

    def configure(self,
                  fx: Position = None,
                  fy: Position = None,
                  font_size: FontSize = None,
                  color: Color = None,
                  bg_color: Color = None):
        """
        Configure viewport display attributes.

        :param fx: relative horizontal position
        :param fy: relative vertical position
        :param font_size: font size
        :param color: foreground color
        :param bg_color: background color
        :return:
        """
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
        if self.rect is None:
            return
        self.display.surface.fill(self.bg_color, rect=self.rect)

    def text(self, text, duration: Interval = None):
        if self.rect is None:
            return
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

    def hsplit(self, *width_values: Position) -> List['Viewport']:
        """
        Split viewport horizontally into 1 or more sub-viewports.

        When errors are detected returned viewports may be "null" (non-displaying).

        :param width_values: width values, as fractions when <1, or pixels when >=1
        :return: generated sub-viewports
        """
        viewports = []
        available_width = self.rect.width if self.rect is not None else 0
        consumed_width = 0
        for width_value in width_values:
            if width_value <= 0:
                log.error(f'hsplit: negative or zero width value: {width_value}')
                width = None
            elif width_value < 1:
                # Fractional width.
                width = int(width_value * available_width)
            else:
                if width_value != int(width_value):
                    log.error(f'hsplit: bad width pixel value: {width_value}')
                    width = None
                else:
                    width = width_value
            if width is None:
                rect = None
            else:
                if consumed_width > available_width:
                    log.error(f'hsplit: unable to fit viewport (width={width_value}).')
                    rect = None
                    consumed_width = available_width
                else:
                    rect = pygame.Rect(self.rect.left + consumed_width,
                                       self.rect.top,
                                       width,
                                       self.rect.height)
                    consumed_width += width
            viewports.append(self.__class__(self.display, rect))
        return viewports

    def vsplit(self, *height_values: Position) -> List['Viewport']:
        """
        Split viewport vertically into 1 or more sub-viewports.

        When errors are detected returned viewports will have rect==None to make
        them non-displaying.

        :param height_values: height values, as fractions when <1, or pixels when >=1
        :return: generated sub-viewports
        """
        viewports = []
        available_height = self.rect.height if self.rect is not None else 0
        consumed_height = 0
        for height_value in height_values:
            if height_value <= 0:
                log.error(f'vsplit: negative or zero height value: {height_value}')
                height = None
            elif height_value < 1:
                # Fractional height.
                height = int(height_value * available_height)
            else:
                if height_value != int(height_value):
                    log.error(f'vsplit: bad height pixel value: {height_value}')
                    height = None
                else:
                    height = height_value
            if height is None:
                rect = None
            else:
                if consumed_height + height > available_height:
                    log.error(f'vsplit: unable to fit viewport (height={height_value}).')
                    rect = None
                    consumed_height = available_height
                else:
                    rect = pygame.Rect(self.rect.left,
                                       self.rect.top + consumed_height,
                                       self.rect.width,
                                       height)
                    consumed_height += height
            viewports.append(self.__class__(self.display, rect))
        return viewports

    def overlay(self) -> 'Viewport':
        """
        Create overlay viewport positioned in the same screen rectangle.

        :return: new Viewport
        """
        return self.__class__(self.display, self.rect)

    def __str__(self):
        return 'Viewport(rect={}, fx={}, fy={}, color={}, bg_color={})'.format(
                    self.rect, self.fx, self.fy, self.color, self.bg_color)
