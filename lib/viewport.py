# Copyright (C) 2021, Steven Cooper
#
# This file is part of rpi-clock.
#
# Rpi-clock is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Rpi-clock is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rpi-clock.  If not, see <https://www.gnu.org/licenses/>.

"""Viewport support for screen display regions."""

import os
import pygame
from typing import Optional, List

from . import log
from .display import Display, \
    COLOR_DEFAULT_FOREGROUND, COLOR_DEFAULT_BACKGROUND, COLOR_DEFAULT_BORDER
from .event_manager import EventManager
from .typing import Color, FontSize, Position, Rect, Interval, Margins
from .utility import sub_rect


# noinspection DuplicatedCode
class Viewport:
    """Viewport is a screen display region."""

    def __init__(self,
                 display: Display,
                 event_manager: EventManager,
                 rect: Optional[Rect]):
        """
        Construct viewport.

        :param display: display for text, image, etc.
        :param event_manager: event manager for setting up handlers
        :param rect: rectangle to frame displayed object (None for "null" viewport)
        """
        self.display = display
        self.event_manager = event_manager
        self.rect = rect
        self.inner_rect = self.rect
        self.font_path: Optional[str] = None
        self.font_size = self.rect.height
        self.fx = 0
        self.fy = 0
        self.color = COLOR_DEFAULT_FOREGROUND
        self.bg_color = COLOR_DEFAULT_BACKGROUND
        self.border_color = COLOR_DEFAULT_BORDER
        self.margins: Optional[Margins] = None
        self._font = None

    def configure(self,
                  fx: Position = None,
                  fy: Position = None,
                  font_path: str = None,
                  font_size: FontSize = None,
                  color: Color = None,
                  bg_color: Color = None,
                  border_color: Color = None,
                  margins: Margins = None):
        """
        Configure viewport display attributes.

        :param fx: relative horizontal position
        :param fy: relative vertical position
        :param font_path: font file path
        :param font_size: font size
        :param color: foreground color
        :param bg_color: background color
        :param border_color: border color
        :param margins: margin spec - all_margins, (horizontal, vertical), or (left, top, right, bottom)
        """
        if fx is not None:
            self.fx = fx
        if fy is not None:
            self.fy = fy
        if font_path is not None:
            self.font_path = font_path
        if font_size is not None:
            self.font_size = font_size
        if color is not None:
            self.color = color
        if bg_color is not None:
            self.bg_color = bg_color
        if border_color is not None:
            self.border_color = border_color
        self.margins = margins
        self.inner_rect = sub_rect(self.rect, margins=self.margins)
        # Discard font cache in case font parameters have changed.
        self._font = None

    @property
    def font(self) -> pygame.font.Font:
        """
        Viewport font property.

        :return: assigned viewport font.
        """
        if self._font is None:
            self._font = pygame.font.Font(self.font_path, self.font_size)
        return self._font

    def clear(self):
        """Clear viewport based on configured background and or border colors."""
        if self.rect is None:
            return
        if (self.border_color == self.bg_color
            or (self.inner_rect.width == self.rect.width
                and self.inner_rect.height == self.rect.height)):
            self.display.surface.fill(self.bg_color, rect=self.rect)
        else:
            self.display.surface.fill(self.border_color, rect=self.rect)
            self.display.surface.fill(self.bg_color, rect=self.inner_rect)

    def text(self,
             text: str,
             duration: Interval = None,
             overwrite: bool = False,
             color: Color = None):
        """
        Display text in viewport.

        :param text: text to display
        :param duration: optional duration before clearing
        :param overwrite: optional boolean to disable clearing the viewport
        :param color: optional text color
        """
        if self.rect is None:
            return
        if not overwrite:
            self.clear()
        while True:
            text_width, text_height = self.font.size(text)
            text_rect = sub_rect(self.rect,
                                 fleft=self.fx,
                                 ftop=self.fy,
                                 width=text_width,
                                 height=text_height,
                                 margins=self.margins)
            if text_rect.width <= self.inner_rect.width:
                break
            shortened_text = text[:-4] if text.endswith('...') else text[:-1]
            if len(shortened_text) == 0:
                break
            text = f'{shortened_text}...'
        if color is None:
            color = self.color
        text_surface = self.font.render(text, True, color)
        self.display.surface.blit(text_surface, text_rect)
        pygame.display.update()
        if duration is not None:
            self.event_manager.register('timer', self.clear, duration, max_count=1)

    def image(self,
              path: str,
              duration: Interval = None,
              overwrite: bool = False):
        """
        Display image file in viewport.

        :param path: image file path
        :param duration: optional duration before clearing
        :param overwrite: optional boolean to disable clearing the viewport
        """
        if self.rect is None:
            return
        if not path or not os.path.isfile(path):
            log.error(f'Image file is missing: {path}')
            self.text('*missing*', duration=duration, overwrite=overwrite)
            return
        if not overwrite:
            self.clear()
        image_surface = pygame.image.load(path)
        # Supposedly speeds rendering to let surface perform conversion.
        if path.lower().endswith('.png'):
            image_surface = image_surface.convert_alpha()
        else:
            image_surface = image_surface.convert()
        image_rect = sub_rect(self.rect,
                              fleft=self.fx,
                              ftop=self.fy,
                              margins=self.margins)
        self.display.surface.blit(image_surface, image_rect)
        pygame.display.update()
        if duration is not None:
            self.event_manager.register('timer', self.clear, duration, max_count=1)

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
            viewports.append(self.__class__(self.display, self.event_manager, rect))
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
            viewports.append(self.__class__(self.display, self.event_manager, rect))
        return viewports

    def overlay(self,
                fx: Position = None,
                fy: Position = None,
                font_path: str = None,
                font_size: FontSize = None,
                color: Color = None,
                bg_color: Color = None,
                border_color: Color = None,
                margins: Margins = None) -> 'Viewport':
        """
        Create overlay viewport positioned in the same screen rectangle.

        For now this is the only way to use alternate fonts and colors in the
        same screen location.

        Also copies or overrides viewport configuration data.

        :param fx: relative horizontal position
        :param fy: relative vertical position
        :param font_path: font file path
        :param font_size: font size
        :param color: foreground color
        :param bg_color: background color
        :param border_color: border color
        :param margins: margin spec - all_margins, (horizontal, vertical), or (left, top, right, bottom)
        :return: new Viewport
        """
        overlay_viewport = self.__class__(self.display, self.event_manager, self.rect)
        overlay_viewport.configure(
            fx=fx if fx is not None else self.fx,
            fy=fy if fy is not None else self.fy,
            font_path=font_path if font_path is not None else self.font_path,
            font_size=font_size if font_size is not None else self.font_size,
            color=color if color is not None else self.color,
            bg_color=bg_color if bg_color is not None else self.bg_color,
            border_color=color if border_color is not None else self.border_color,
            margins=color if margins is not None else self.margins)
        return overlay_viewport

    def __str__(self) -> str:
        """
        String representation for logging.

        :return: string representing object
        """
        return 'Viewport(rect={}, fx={}, fy={}, color={}, bg_color={})'.format(
                    self.rect, self.fx, self.fy, self.color, self.bg_color)
