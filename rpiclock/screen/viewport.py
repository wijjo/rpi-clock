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
from typing import Optional, List

from rpiclock.drivers import Display
from rpiclock.events import EventProducersRegistry
from rpiclock.utility import log, Rect, Font
from rpiclock.utility.typing import Color, FontSize, Position, Interval, Margins

from .constants import COLOR_DEFAULT_FOREGROUND, COLOR_DEFAULT_BACKGROUND, COLOR_DEFAULT_BORDER


# noinspection DuplicatedCode
class Viewport:
    """Viewport is a screen display region."""

    def __init__(self,
                 display: Display,
                 event_producers_registry: EventProducersRegistry,
                 rect: Optional[Rect]):
        """
        Construct viewport.

        :param display: display for text, image, etc.
        :param event_producers_registry: event manager for setting up handlers
        :param rect: rectangle to frame displayed object (None for "null" viewport)
        """
        self.display = display
        self.event_producers_registry = event_producers_registry
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
        self.inner_rect = self.rect.sub_rect(margins=self.margins)
        # Discard font cache in case font parameters have changed.
        self._font = None

    @property
    def font(self) -> Font:
        """
        Viewport font property.

        :return: assigned viewport font.
        """
        if self._font is None:
            self._font = self.display.get_font(self.font_path, self.font_size)
        return self._font

    def clear(self):
        """Clear viewport based on configured background and or border colors."""
        if self.rect is None:
            return
        if (self.border_color == self.bg_color
            or (self.inner_rect.width == self.rect.width
                and self.inner_rect.height == self.rect.height)):
            self.display.fill_rectangle(self.bg_color, rect=self.rect)
        else:
            self.display.fill_rectangle(self.border_color, rect=self.rect)
            self.display.fill_rectangle(self.bg_color, rect=self.inner_rect)

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
            # noinspection PyBroadException
            try:
                text_size = self.display.measure_text(text, self.font)
            except Exception as exc:
                log.error('Bad text for display.', exc, text)
                text = '???'
                text_size = self.display.measure_text(text, self.font)
            text_rect = self.rect.sub_rect(fleft=self.fx,
                                           ftop=self.fy,
                                           width=text_size.width,
                                           height=text_size.height,
                                           margins=self.margins)
            if text_rect.width <= self.inner_rect.width:
                break
            shortened_text = text[:-4] if text.endswith('...') else text[:-1]
            if len(shortened_text) == 0:
                break
            text = f'{shortened_text}...'
        if color is None:
            color = self.color
        self.display.render_text(text, self.font, text_rect, color)
        if duration is not None:
            self.event_producers_registry.register('timer', self.clear, duration, max_count=1)

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
        image_rect = self.rect.sub_rect(fleft=self.fx, ftop=self.fy, margins=self.margins)
        self.display.render_image(path, image_rect)
        if duration is not None:
            self.event_producers_registry.register('timer', self.clear, duration, max_count=1)

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
                    rect = Rect(self.rect.left + consumed_width,
                                self.rect.top,
                                width,
                                self.rect.height)
                    consumed_width += width
            viewports.append(self.__class__(self.display, self.event_producers_registry, rect))
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
                    rect = Rect(self.rect.left,
                                self.rect.top + consumed_height,
                                self.rect.width,
                                height)
                    consumed_height += height
            viewports.append(self.__class__(self.display, self.event_producers_registry, rect))
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
        Create overlay viewport positioned at the same screen rectangle.

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
        overlay_viewport = self.__class__(self.display, self.event_producers_registry, self.rect)
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
