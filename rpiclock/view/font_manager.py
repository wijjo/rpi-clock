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


class FontManager:
    """Font manager is responsible for finding font resources."""

    def __init__(self, folder: str):
        """
        Font manager constructor.

        :param folder: font resource root folder
        """
        self.fonts_by_name: Dict[str, str] = {}
        for dir_path, dir_names, file_names in os.walk(folder):
            for file_name in file_names:
                base_name, extension = os.path.splitext(file_name)
                if extension.lower() in ['.otf', '.ttf']:
                    file_path = os.path.join(dir_path, file_name)
                    self.fonts_by_name[base_name.lower()] = file_path

    def get_font_path(self, name: str) -> Optional[str]:
        """
        Look up font path based on name.

        :param name: font name
        :return: path or None if not found
        """
        return self.fonts_by_name.get(name.lower())
