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

"""Font manager class."""

import os
from typing import Dict, Optional

from .display import FONT_DEFAULT_NAME


class FontManager:
    """Font manager is responsible for finding font resources."""

    def __init__(self, folder: str):
        """
        Font manager constructor.

        :param folder: font resource root folder
        """
        self.fonts_by_name: Dict[str, str] = {}
        self.default_font_path: Optional[str] = None
        for dir_path, dir_names, file_names in os.walk(folder):
            for file_name in file_names:
                base_name, extension = os.path.splitext(file_name)
                base_name = base_name.lower()
                if extension.lower() in ['.otf', '.ttf']:
                    file_path = os.path.join(dir_path, file_name)
                    self.fonts_by_name[base_name] = file_path
                    if base_name == FONT_DEFAULT_NAME:
                        self.default_font_path = file_path
        if self.default_font_path is None:
            raise RuntimeError(f'Failed to resolve default font path for "{FONT_DEFAULT_NAME}".')

    def get_font_path(self, name: str) -> str:
        """
        Look up font path based on name.

        Return the default font if not found.

        :param name: font name
        :return: path or None if not found
        """
        font_path = self.fonts_by_name.get(name.lower())
        if font_path is None:
            font_path = self.default_font_path
        return font_path
