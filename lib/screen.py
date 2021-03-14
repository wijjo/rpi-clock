from dataclasses import dataclass
from typing import Dict, Optional

from . import log
from .config import Config
from .event_manager import EventManager
from .font_manager import FontManager
from .panel import Panel
from .panels.message import MessagePanel
from .typing import Interval, Position, FontSize, Color, Margins
from .viewport import Viewport


@dataclass
class ScreenBlock:
    name: str
    viewport: Viewport
    panel: Panel = None


class Screen:

    def __init__(self,
                 config: Config,
                 event_manager: EventManager,
                 font_manager: FontManager):
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
        self.on_create_panels()
        for block in self.blocks.values():
            block.panel.on_initialize_events(self.event_manager)
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
                           font_name: str = None,
                           font_size: FontSize = None,
                           color: Color = None,
                           bg_color: Color = None,
                           border_color: Color = None,
                           margins: Margins = None):
        """
        Configure viewport display attributes.

        :param name: viewport name
        :param fx: relative horizontal position
        :param fy: relative vertical position
        :param font_name: font name
        :param font_size: font size
        :param color: foreground color
        :param bg_color: background color
        :param border_color: border color
        :param margins: margin spec - all_margins, (horizontal, vertical), or (left, top, right, bottom)
        """
        font_path = self.font_manager.get_font_path(font_name)
        self.get_block(name).viewport.configure(fx=fx,
                                                fy=fy,
                                                font_path=font_path,
                                                font_size=font_size,
                                                color=color,
                                                bg_color=bg_color,
                                                border_color=border_color,
                                                margins=margins)

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

    def on_create_panels(self):
        """
        Required hook for sub-class panel panel.
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
