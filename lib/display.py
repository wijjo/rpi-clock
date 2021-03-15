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

import os
import pygame

# Defaults and constants.
COLOR_DEFAULT_FOREGROUND = (255, 255, 255)
COLOR_DEFAULT_BACKGROUND = (0, 0, 0)
COLOR_DEFAULT_BORDER = COLOR_DEFAULT_BACKGROUND
COLOR_GHOST_TEXT = (25, 25, 25)


class Display:
    """Display screen class."""

    def __init__(self,
                 left: int,
                 top: int,
                 width: int,
                 height: int,
                 device: str,
                 driver: str):
        """
        Display constructor.

        :param left: screen left (usually 0)
        :param top: screen top (usually 0)
        :param width: screen width in pixels
        :param height: screen height in pixels
        :param device: device name, e.g. "/dev/fb1"
        :param driver: driver name, e.g. "fbcon"
        """
        self.rect = pygame.Rect(left, top, width, height)
        os.putenv('SDL_FBDEV', device)
        os.putenv('SDL_VIDEODRIVER', driver)
        pygame.font.init()
        pygame.display.init()
        pygame.mouse.set_visible(False)
        self.bg_color = COLOR_DEFAULT_BACKGROUND
        self.surface = pygame.display.set_mode((self.rect.width, self.rect.height))

    @staticmethod
    def shut_down():
        """Handle clean shutdown."""
        pygame.display.quit()
        pygame.font.quit()

    def clear(self):
        """Clear screen."""
        self.surface.fill(self.bg_color)
        pygame.display.update()
