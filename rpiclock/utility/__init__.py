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

"""Utility package."""

from dataclasses import dataclass

from .color_resolver import ColorResolver, NAMED_COLORS
from .config import Config, ConfigDict
from .data_source import DataSource, JSONDataSource, ImageDataSource
from .fonts_finder import FontsFinder, FONT_DEFAULT_NAME, FONT_DEFAULT_SIZE
from .logger import log
from .rect import Rect
from .timer import Timer


@dataclass
class Dimensions:
    """Display dimensions data."""
    width: int
    height: int


class Font:
    """Base stub class for a font."""
    pass
