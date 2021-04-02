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
from typing import Dict, Optional, Callable

from rpiclock.events import EventProducersRegistry
from rpiclock.utility import log, Config, FontsFinder, FONT_DEFAULT_SIZE
from rpiclock.utility.typing import Interval, Position, Color, Margins

from .panel import Panel
from .viewport import Viewport


@dataclass
class ScreenBlock:
    name: str
    viewport: Viewport
    panel: Panel = None


class Screen:
    """Application screen."""

    def __init__(self,
                 name: str,
                 config: Config,
                 event_producers_registry: EventProducersRegistry,
                 font_manager: FontsFinder):
        """
        Application screen constructor.

        :param name: screen name
        :param config: configuration data
        :param event_producers_registry: event manager for registering handled events
        :param font_manager: font manager for access to font resources
        """
        self.name = name
        self.config = config
        self.event_producers_registry = event_producers_registry
        self.font_manager = font_manager
        self.blocks: Optional[Dict[str, ScreenBlock]] = None
        self.outer_viewport: Optional[Viewport] = None
        self.set_message_function: Optional[Callable[[str, Interval], None]] = None

    def get_block(self, name: str) -> ScreenBlock:
        """
        Get block (viewport/panel combination) by name.

        :param name: block name
        :return: block
        :raise KeyError: if name not found
        """
        return self.blocks[name]

    def initialize(self, outer_viewport: Viewport):
        """
        Base screen initialization.

        :param outer_viewport: outer viewport to sub-divide
        """
        self.on_initialize_events()
        self.outer_viewport = outer_viewport
        self.initialize_blocks()
        self.event_producers_registry.register('tick', self.on_tick)

    def initialize_blocks(self):
        self.blocks = {}
        self.on_initialize_viewports(self.outer_viewport)
        self.on_initialize_panels()
        for block in self.blocks.values():
            block.panel.on_initialize(self.event_producers_registry, block.viewport)
        self.update_viewports()

    def add_viewport(self, name: str, viewport: Viewport):
        """
        Register a named viewport.

        :param name: viewport name
        :param viewport: viewport
        """
        self.blocks[name] = ScreenBlock(name, viewport)

    def configure_panel(self,
                        panel: Panel,
                        name: str,
                        fx: Position = None,
                        fy: Position = None,
                        font: str = None,
                        color: Color = None,
                        bg_color: Color = None,
                        border_color: Color = None,
                        margins: Margins = None):
        """
        Configure viewport panel and its display attributes.

        :param panel: panel to display in the viewport
        :param name: viewport name
        :param fx: relative horizontal position
        :param fy: relative vertical position
        :param font: font name:size specification
        :param color: foreground color
        :param bg_color: background color
        :param border_color: border color
        :param margins: margin spec - all_margins, (horizontal, vertical), or (left, top, right, bottom)
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
        self.get_block(name).panel = panel
        # The set_message() method is used to identify a proper message panel.
        if hasattr(panel, 'set_message'):
            self.set_message_function = panel.set_message

    def refresh(self):
        """Refresh screen."""
        self.initialize_blocks()

    def update_viewports(self, check: bool = False):
        """
        Update viewports.

        :param check: check before updating if True
        """
        for block in self.blocks.values():
            if not check or block.panel.on_check():
                block.panel.on_display(block.viewport)

    def on_initialize_events(self):
        """Required event initialization hook."""
        raise NotImplementedError

    def on_initialize_viewports(self, outer_viewport: Viewport):
        """
        Required viewport initialization hook.

        :param outer_viewport: outer viewport to sub-divide
        """
        raise NotImplementedError

    def on_initialize_panels(self):
        """Required panel initialization hook."""
        raise NotImplementedError

    def on_tick(self):
        """Periodic panel update hook."""
        self.update_viewports(check=True)

    def message(self, text: str, duration: Interval = None):
        """
        Display information messages on the screen.

        Looks for a viewport/panel named 'message'.

        :param text: text message to display
        :param duration: optional duration before it gets cleared
        """
        log.info(f'Message: {text}')
        if self.set_message_function is not None:
            self.set_message_function(text, duration)
