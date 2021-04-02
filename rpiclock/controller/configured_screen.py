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

"""Screen that is completely defined by configuration data."""

from typing import List

from rpiclock.events import EventProducersRegistry
from rpiclock.panels import PanelRegistry
from rpiclock.screen import Screen, Viewport
from rpiclock.utility import Config, ConfigDict, log, FontsFinder, ColorResolver


class ConfiguredScreen(Screen):

    """Screen that is completely specified by configuration data."""

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
        super().__init__(name, config, event_producers_registry, font_manager)
        self.color_resolver = ColorResolver()
        # Add theme colors so that they can be resolved as named colors.
        if self.config.theme and self.config.themes:
            theme = self.config.themes.get(self.config.theme)
            for name, value in theme.items():
                self.color_resolver.add(name, value)

    def on_initialize_events(self):
        """Required event initialization hook."""
        pass

    def on_initialize_viewports(self, outer_viewport: Viewport):
        """
        Required viewport initialization hook.

        Note that this assumes the outer division is vertical rows, and that
        columns and rows are alternated. I.e. a row may not have sub-rows and a
        column may not have sub-columns.

        :param outer_viewport: viewport that provides outer dimensions
        """
        log.info(f'Initialize screen "{self.name}" viewports.')
        self._initialize_viewport(outer_viewport,
                                  self.config.screens[self.name],
                                  True)

    def on_initialize_panels(self):
        """Required panel initialization hook."""
        pass

    def _initialize_viewport(self,
                             viewport: Viewport,
                             viewport_config: ConfigDict,
                             vertical: bool):
        if viewport_config.panel:
            self._initialize_panel(viewport_config.panel, viewport)
        self._initialize_sub_viewports(viewport, viewport_config, vertical)

    def _initialize_panel(self, panel_config: ConfigDict, viewport: Viewport):
        if not panel_config['class']:
            log.error(f'Panel configuration has no "class" element.')
            return
        panel_class_name = panel_config['class']
        panel_class = PanelRegistry.get_panel_class(panel_class_name)
        if not panel_class:
            log.error(f'Unknown panel class "{panel_class_name}".')
            return
        if not panel_config.name:
            log.error('Ignoring panel with no name.')
            return
        # First grab any global params for the panel class name.
        params = dict(self.config.panel_params.get(panel_class_name, {}))
        if panel_config.params:
            params.update(panel_config.params)
        try:
            # noinspection PyArgumentList
            panel = panel_class(**params)
            log.info(f'Initialize {panel_class.__name__} panel "{panel_config.name}".')
            self.add_viewport(panel_config.name, viewport)
            self.configure_panel(
                panel,
                panel_config.name,
                fx=panel_config.fx,
                fy=panel_config.fy,
                font=panel_config.font,
                color=self.color_resolver.resolve(panel_config.color),
                bg_color=self.color_resolver.resolve(panel_config.bg_color),
                border_color=self.color_resolver.resolve(panel_config.border_color),
                margins=panel_config.margins)
        except (TypeError, ValueError) as exc:
            exc_text = str(exc)
            if exc_text.startswith('__init__() '):
                exc_text = exc_text[11:]
            log.error(f'Failed to construct "{panel_class_name}" panel'
                      f' ({panel_class.__name__}): {exc_text}')
            return

    def _initialize_sub_viewports(self,
                                  viewport: Viewport,
                                  viewport_config: ConfigDict,
                                  vertical: bool):
        if vertical:
            sub_name = 'rows'
            size_name = 'height'
            split_method = viewport.vsplit
        else:
            sub_name = 'columns'
            size_name = 'width'
            split_method = viewport.hsplit

        # Done if there are no sub-viewports to deal with.
        sub_configs = viewport_config[sub_name]
        if not sub_configs:
            return

        # Gather explicitly-sized primary viewport configurations and sizes.
        primary_sub_configs: List[ConfigDict] = []
        sizes: List[int] = []
        for sub_config in sub_configs:
            if sub_config[size_name]:
                primary_sub_configs.append(sub_config)
                sizes.append(sub_config[size_name])

        # Split primary sub-viewports.
        primary_viewports = split_method(*sizes)

        # Gather all viewports for recursive processing, including overlays.
        all_viewports: List[Viewport] = []
        primary_idx = -1
        for sub_config in sub_configs:
            if sub_config[size_name] is not None:
                primary_idx += 1
                all_viewports.append(primary_viewports[primary_idx])
            else:
                all_viewports.append(primary_viewports[primary_idx].overlay())

        # Recursively initialize and split sub-viewports.
        for viewport_idx in range(len(sub_configs)):
            self._initialize_viewport(all_viewports[viewport_idx],
                                      sub_configs[viewport_idx],
                                      not vertical)
