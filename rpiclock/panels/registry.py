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

"""Panel registry."""

from typing import Dict, Callable, Type, Optional

from rpiclock.screen import Panel


class PanelRegistry:

    panels: Dict[str, Type[Panel]] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[Type[Panel]], Type[Panel]]:
        """
        Decorator for registering a panel class.

        :param name: panel name
        :return: inner function that registers the class
        """
        def _inner(panel_cls: Type[Panel]) -> Type[Panel]:
            cls.panels[name] = panel_cls
            return panel_cls
        return _inner

    @classmethod
    def get_panel_class(cls, name: str) -> Optional[Type[Panel]]:
        """
        Look up panel class by name.

        :param name: panel name
        :return: panel class if found or None if not
        """
        return cls.panels.get(name)
