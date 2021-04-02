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

"""Display representing a physical screen device."""

from rpiclock.utility import Rect, Font, Dimensions
from rpiclock.utility.typing import Color


class Display:
    """Base display screen class."""

    def __init__(self, left: int, top: int, width: int, height: int):
        """
        Display constructor.

        :param left: screen left (usually 0)
        :param top: screen top (usually 0)
        :param width: screen width in pixels
        :param height: screen height in pixels
        """
        self.rect = Rect(left, top, width, height)

    def shut_down(self):
        """Required override to handle clean shutdown."""
        raise NotImplementedError

    def get_font(self, path: str, size: int) -> Font:
        """
        Required override to provide font object by path and size.

        :param path: font file path
        :param size: font size
        :return: font object
        """
        raise NotImplementedError

    def measure_text(self, text: str, font: Font) -> Dimensions:
        """
        Required override to calculate displayed text size.

        :param text: text that will be displayed
        :param font: font that will be used for rendering
        :return: text dimensions
        """
        raise NotImplementedError

    def render_text(self, text: str, font: Font, rect: Rect, color: Color):
        """
        Required override to render text.

        :param text: text to render
        :param font: display font
        :param rect: rectangle to target for rendering
        :param color: text color
        """
        raise NotImplementedError

    def fill_rectangle(self, color: Color, rect: Rect):
        """
        Required override to fill rectangle with color.

        :param color: color to use
        :param rect: rectangle to fill
        """
        raise NotImplementedError

    def render_image(self, path: str, rect: Rect):
        """
        Render image file.

        :param path: image file path
        :param rect: image display rectangle
        """
        raise NotImplementedError
