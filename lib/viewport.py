import pygame
from typing import Optional, List

from . import log
from .display import Display, COLOR_DEFAULT_TEXT, COLOR_DEFAULT_BACKGROUND
from .typing import Color, FontSize, Position, Rect, Duration
from .utility import sub_rect


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
        self.color = COLOR_DEFAULT_TEXT
        self.bg_color = COLOR_DEFAULT_BACKGROUND
        self._font = None

    def configure(self,
                  fx: Position = None,
                  fy: Position = None,
                  font_size: FontSize = None,
                  color: Color = None,
                  bg_color: Color = None):
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

    def text(self, text, duration: Duration = None):
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

    def hsplit(self, *splits: Position) -> List['Viewport']:
        """
        Split viewport horizontally into 2 or more sub-viewports.

        When errors are detected returned viewports may be "null" (non-displaying).

        :param splits: split values, as fractions when <1, or pixels when >=1
        :return: generated sub-viewports (quantity is len(splits) + 1
        """
        viewports = []
        available_width = self.rect.width if self.rect is not None else 0
        consumed_width = 0
        for split in splits:
            if split <= 0:
                log.error(f'hsplit: negative or zero split value: {split}')
                width = None
            elif split < 1:
                # Fractional split.
                width = int(split * available_width)
            else:
                if split != int(split):
                    log.error(f'hsplit: bad split pixel value: {split}')
                    width = None
                else:
                    width = split
            if width is None:
                rect = None
            else:
                if consumed_width + width > available_width:
                    log.error(f'hsplit: unable to fit viewport (split={split}).')
                    consumed_width = available_width
                    rect = None
                else:
                    rect = pygame.Rect(self.rect.left + consumed_width,
                                       self.rect.top,
                                       width,
                                       self.rect.height)
                    consumed_width += width
            viewports.append(self.__class__(self.display, rect))
        if consumed_width >= available_width:
            log.error('hsplit: unable to fit last viewport.')
            rect = None
        else:
            width = available_width - consumed_width
            rect = pygame.Rect(self.rect.right - width,
                               self.rect.top,
                               width,
                               self.rect.height)
        viewports.append(self.__class__(self.display, rect))
        return viewports

    def vsplit(self, *splits: Position) -> List['Viewport']:
        """
        Split viewport vertically into 2 or more sub-viewports.

        When errors are detected returned viewports will have rect==None to make
        them non-displaying.

        :param splits: split values, as fractions when <1, or pixels when >=1
        :return: generated sub-viewports (quantity is len(splits) + 1
        """
        viewports = []
        available_height = self.rect.height if self.rect is not None else 0
        consumed_height = 0
        for split in splits:
            if split <= 0:
                log.error(f'vsplit: negative or zero split value: {split}')
                height = None
            elif split < 1:
                # Fractional split.
                height = int(split * available_height)
            else:
                if split != int(split):
                    log.error(f'vsplit: bad split pixel value: {split}')
                    height = None
                else:
                    height = split
            if height is None:
                rect = None
            else:
                if consumed_height + height > available_height:
                    log.error(f'vsplit: unable to fit viewport (split={split}).')
                    consumed_height = available_height
                    rect = None
                else:
                    rect = pygame.Rect(self.rect.left,
                                       self.rect.top + consumed_height,
                                       self.rect.width,
                                       height)
                    consumed_height += height
            viewports.append(self.__class__(self.display, rect))
        if consumed_height >= available_height:
            log.error('vsplit: unable to fit last viewport.')
            rect = None
        else:
            height = available_height - consumed_height
            rect = pygame.Rect(self.rect.left,
                               self.rect.bottom - height,
                               self.rect.width,
                               height)
        viewports.append(self.__class__(self.display, rect))
        return viewports

    def __str__(self):
        return 'Viewport(rect={}, fx={}, fy={}, color={}, bg_color={})'.format(
                    self.rect, self.fx, self.fy, self.color, self.bg_color)
