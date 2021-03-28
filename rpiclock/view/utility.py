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

from dataclasses import dataclass
from typing import Optional

from rpiclock import log
from rpiclock.typing import Margins


@dataclass
class Rect:
    """Screen rectangle data."""
    left: int
    top: int
    width: int
    height: int

    def sub_rect(self,
                 left: int = None,
                 top: int = None,
                 width: int = None,
                 height: int = None,
                 fleft: float = None,
                 ftop: float = None,
                 fwidth: float = None,
                 fheight: float = None,
                 margins: Margins = None,
                 ) -> 'Rect':
        """
        Calculate and produce a sub-rectangle based on various ways of specifying offsets.

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
        inner_rect = self.inner_rect(margins)
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
        ret_rect = Rect(left, top, width, height)
        return ret_rect

    def inner_rect(self, margins: Optional[Margins]) -> 'Rect':
        """
        Calculate an inner rectangle based on flexible margin data.

        :param margins: margins to use for adjustment
        :return: adjusted inner rectangle
        """
        # A single integer is applied to all offsets.
        if isinstance(margins, int):
            return Rect(self.left + margins,
                        self.top + margins,
                        self.width - (2 * margins),
                        self.height - (2 * margins))
        # An integer pair is applied equally to horizontal and vertical offsets.
        if isinstance(margins, (tuple, list)) and len(margins) == 2:
            return Rect(self.left + margins[0],
                        self.top + margins[1],
                        self.width - (2 * margins[0]),
                        self.height - (2 * margins[1]))
        # 4 integers is (left, top, right, bottom)
        elif isinstance(margins, (tuple, list)) and len(margins) == 4:
            return Rect(self.left + margins[0],
                        self.top + margins[1],
                        self.width - (margins[0] + margins[2]),
                        self.height - (margins[1] + margins[3]))
        # Anything other than None is an error. Return the same rectangle.
        if margins is not None:
            log.error(f'Bad margins value: {margins}')
        return Rect(self.left, self.top, self.width, self.height)


@dataclass
class Dimensions:
    """Display dimensions data."""
    width: int
    height: int


class Font:
    """Base stub class for a font."""
    pass
