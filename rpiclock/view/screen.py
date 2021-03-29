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

"""A screen is a full-screen application page."""

from dataclasses import dataclass
from typing import Dict, Optional

from rpiclock import log
from rpiclock.controller.event_manager import EventManager
from rpiclock.model.config import Config
from rpiclock.model.panel import Panel
from rpiclock.controller.panels.message import MessagePanel
from rpiclock.typing import Interval, Position, Color, Margins

from .display import FONT_DEFAULT_SIZE
from .font_manager import FontManager
from .viewport import Viewport


@dataclass
class ScreenBlock:
    name: str
    viewport: Viewport
    panel: Panel = None


class Screen:
    """Application screen."""

    def __init__(self,
                 config: Config,
                 event_manager: EventManager,
                 font_manager: FontManager):
        """
        Application screen constructor.

        :param config: configuration data
        :param event_manager: event manager for registering handled events
        :param font_manager: font manager for access to font resources
        """
        self.config = config
        self.event_manager = event_manager
        self.font_manager = font_manager
        self.blocks: Dict[str, ScreenBlock] = {}
        self.message_panel: Optional[MessagePanel] = None

    def get_block(self, name: str) -> ScreenBlock:
        """
        Get block (viewport/panel combination) by name.

        :param name: block name
        :return: block
        :raise KeyError: if name not found
        """
        return self.blocks[name]

    def set_panel(self, name: str, panel: Panel):
        """
        Assign panel to viewport.

        :param name: block name to assign panel
        :param panel: panel to assign
        """
        self.get_block(name).panel = panel
        if isinstance(panel, MessagePanel):
            self.message_panel = panel

    def initialize(self, outer_viewport: Viewport):
        """
        Base screen initialization.
        """
        self.on_initialize_events()
        self.event_manager.register('tick', self.on_tick)
        self.on_create_viewports(outer_viewport)
        self.on_configure_viewports()
        for block in self.blocks.values():
            block.panel.on_initialize(self.event_manager, block.viewport)
        self.update_viewports()

    def add_viewport(self, name: str, viewport: Viewport):
        """
        Register a named viewport.

        :param name: viewport name
        :param viewport: viewport
        """
        self.blocks[name] = ScreenBlock(name, viewport)

    def configure_viewport(self,
                           name: str,
                           fx: Position = None,
                           fy: Position = None,
                           font: str = None,
                           color: Color = None,
                           bg_color: Color = None,
                           border_color: Color = None,
                           margins: Margins = None,
                           panel: Panel = None):
        """
        Configure viewport display attributes.

        :param name: viewport name
        :param fx: relative horizontal position
        :param fy: relative vertical position
        :param font: font name:size specification
        :param color: foreground color
        :param bg_color: background color
        :param border_color: border color
        :param margins: margin spec - all_margins, (horizontal, vertical), or (left, top, right, bottom)
        :param panel: panel to display in the viewport
        """
        try:
            font_name, font_size_string = font.split(':')
            font_path = self.font_manager.get_font_path(font_name)
            font_size = int(font_size_string)
        except ValueError:
            log.error(f'Bad font specification "{font}".')
            font_path = self.font_manager.default_font_path
            font_size = FONT_DEFAULT_SIZE
        self.get_block(name).viewport.configure(fx=fx,
                                                fy=fy,
                                                font_path=font_path,
                                                font_size=font_size,
                                                color=color,
                                                bg_color=bg_color,
                                                border_color=border_color,
                                                margins=margins)
        if panel is not None:
            self.set_panel(name, panel)

    def refresh(self):
        """
        Refresh screen.
        """
        self.on_configure_viewports()
        self.update_viewports()

    def update_viewports(self, check: bool = False):
        """
        Update viewports.

        :param check: check before updating if True
        """
        for block in self.blocks.values():
            if not check or block.panel.on_check():
                block.panel.on_display(block.viewport)

    def on_initialize_events(self):
        """
        Required hook for sub-class event initialization.
        """
        raise NotImplementedError

    def on_create_viewports(self, outer_viewport: Viewport):
        """
        Required hook for sub-class viewport creation.
        """
        raise NotImplementedError

    def on_configure_viewports(self):
        """
        Required hook for sub-class viewport configuration.
        """
        raise NotImplementedError

    def on_tick(self):
        """
        Called to update panels.
        """
        self.update_viewports(check=True)

    def message(self, text: str, duration: Interval = None):
        """
        Display information messages on the screen.

        Looks for a viewport/panel named 'message'.

        :param text: text message to display
        :param duration: optional duration before it gets cleared
        """
        log.info(f'Message: {text}')
        if self.message_panel is not None:
            self.message_panel.set(text, duration=duration)
