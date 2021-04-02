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

"""Display implementation based on PyGame."""

import os
import pygame

from rpiclock.utility import Font, Dimensions, Rect
from rpiclock.utility.typing import Color

from .display import Display


class PygameFont(Font):
    """Pygame font data."""
    def __init__(self, pygame_font: pygame.font.Font):
        self.pygame_font = pygame_font


def _make_pygame_rect(rect: Rect) -> pygame.Rect:
    return pygame.Rect(rect.left, rect.top, rect.width, rect.height)


class PygameDisplay(Display):
    """Pygame display screen class."""

    def __init__(self,
                 left: int,
                 top: int,
                 width: int,
                 height: int,
                 device: str,
                 driver: str):
        """
        Pygame display constructor.

        :param left: screen left (usually 0)
        :param top: screen top (usually 0)
        :param width: screen width in pixels
        :param height: screen height in pixels
        :param device: device name, e.g. "/dev/fb1"
        :param driver: driver name, e.g. "fbcon"
        """
        super().__init__(left, top, width, height)
        os.putenv('SDL_FBDEV', device)
        os.putenv('SDL_VIDEODRIVER', driver)
        pygame.font.init()
        pygame.display.init()
        pygame.mouse.set_visible(False)
        self.surface = pygame.display.set_mode((self.rect.width, self.rect.height))

    def shut_down(self):
        """Required override to handle clean shutdown."""
        pygame.display.quit()
        pygame.font.quit()

    def get_font(self, path: str, size: int) -> PygameFont:
        """
        Required override to provide font object by path and size.

        :param path: font file path
        :param size: font size
        :return: font object
        """
        return PygameFont(pygame.font.Font(path, size))

    def measure_text(self, text: str, font: PygameFont) -> Dimensions:
        """
        Required override to calculate displayed text size.

        :param text: text that will be displayed
        :param font: font that will be used for rendering
        :return: text dimensions
        """
        width, height = font.pygame_font.size(text)
        return Dimensions(width, height)

    def render_text(self, text: str, font: PygameFont, rect: Rect, color: Color):
        """
        Required override to render text.

        :param text: text to render
        :param font: display font
        :param rect: rectangle to target for rendering
        :param color: text color
        """
        text_surface = font.pygame_font.render(text, True, color)
        self.surface.blit(text_surface, _make_pygame_rect(rect))
        pygame.display.update()

    def fill_rectangle(self, color: Color, rect: Rect):
        """
        Required override to fill rectangle with color.

        :param color: color to use
        :param rect: rectangle to fill
        """
        self.surface.fill(color, _make_pygame_rect(rect))
        pygame.display.update()

    def render_image(self, path: str, rect: Rect):
        """
        Render image file.

        :param path: image file path
        :param rect: image display rectangle
        """
        image_surface = pygame.image.load(path)
        # Supposedly speeds rendering to let surface perform conversion.
        if path.lower().endswith('.png'):
            image_surface = image_surface.convert_alpha()
        else:
            image_surface = image_surface.convert()
        self.surface.blit(image_surface, _make_pygame_rect(rect))
        pygame.display.update()
