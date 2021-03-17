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

"""General-purpose utility functions and classes."""

import pygame
from dataclasses import dataclass
from typing import Optional

from rpiclock import log
from rpiclock.typing import Margins


@dataclass
class MarginData:
    """Margin data for specifying PyGame rectangle border."""

    left: int
    top: int
    right: int
    bottom: int

    def adjust_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """
        Produce an inner rectangle based on another rectangle and margin data.

        :param rect: outer rectangle
        :return: inner rectangle
        """
        return pygame.Rect(rect.left + self.left,
                           rect.top + self.top,
                           rect.width - (self.left + self.right),
                           rect.height - (self.top + self.bottom))

    @classmethod
    def from_raw(cls, margins: Optional[Margins]) -> 'MarginData':
        """
        Convert margin spec as tuple, integer, or None to (left, top, right, bottom) tuple.

        :param margins: margin specification
        :return: (left, top, right, bottom) tuple
        """
        if margins is None:
            return cls(0, 0, 0, 0)
        if isinstance(margins, int):
            return cls(margins, margins, margins, margins)
        # Handle lists as tuples, to accommodate data from external configurations.
        if isinstance(margins, (tuple, list)) and len(margins) == 2:
            return cls(margins[0], margins[1], margins[0], margins[1])
        if isinstance(margins, (tuple, list)) and len(margins) == 4:
            return cls(margins[0], margins[1], margins[2], margins[3])
        log.error(f'Bad margins value: {margins}')
        return cls(0, 0, 0, 0)

    def __str__(self):
        """
        Human-friendlier string conversion.

        :return: descriptive string with data
        """
        return f'MarginData(left={self.left}, top={self.top},' \
               f' right={self.right}, bottom={self.bottom}'


def sub_rect(outer_rect: pygame.Rect,
             left: int = None,
             top: int = None,
             width: int = None,
             height: int = None,
             fleft: float = None,
             ftop: float = None,
             fwidth: float = None,
             fheight: float = None,
             margins: Margins = None,
             ) -> pygame.Rect:
    """
    Calculate sub-rect of outer rect based on various ways of specifying offsets.

    :param outer_rect: outer rectangle
    :param left: optional left pixel position
    :param top: optional top pixel position
    :param width: optional pixel width
    :param height: optional pixel height
    :param fleft: optional left position as a fractional float
    :param ftop: optional top position as a fractional float
    :param fwidth: optional width as a fractional float
    :param fheight: optional height as a fractional float
    :param margins: optional full margin specification
    :return:
    """
    margin_data = MarginData.from_raw(margins)
    inner_rect = margin_data.adjust_rect(outer_rect)
    if fwidth is None:
        if width is None:
            width = inner_rect.width
    else:
        width = int(inner_rect.width * fwidth)
    if fheight is None:
        if height is None:
            height = inner_rect.height
    else:
        height = int(inner_rect.height * fheight)
    if fleft is None:
        if left is None:
            left = inner_rect.left
        else:
            left = inner_rect.left + left
    else:
        left = inner_rect.left + int(fleft * (inner_rect.width - width))
    if ftop is None:
        if top is None:
            top = inner_rect.top
        else:
            top = inner_rect.top + top
    else:
        top = inner_rect.top + int(ftop * (inner_rect.height - height))
    ret_rect = pygame.Rect(left, top, width, height)
    return ret_rect
