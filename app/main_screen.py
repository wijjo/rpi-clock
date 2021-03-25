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

"""Main (default) rpi-clock screen."""

from rpiclock import log
from rpiclock.controller.panels.message import MessagePanel
from rpiclock.controller.panels.time import TimePanel
from rpiclock.controller.panels.weather import WeatherPanel
from rpiclock.view.screen import Screen
from rpiclock.view.viewport import Viewport


class MainScreen(Screen):
    """Main clock/calendar/weather screen."""

    def on_initialize_events(self):
        """Required call-back to set up event handlers."""
        pass

    def on_create_viewports(self, outer_viewport: Viewport):
        """
        Required call-back to create named viewports.

        :param outer_viewport: viewport that provides outer dimensions
        """
        log.info('Create main screen viewports.')
        rows = outer_viewport.vsplit(*self.config.rows)
        self.add_viewport('time', rows[0])
        row2_columns = rows[1].hsplit(self.config.panels.date.width,
                                      self.config.panels.seconds.width)
        self.add_viewport('date', row2_columns[0])
        self.add_viewport('seconds', row2_columns[1])
        row3_columns = rows[2].hsplit(self.config.panels.temperature.width,
                                      self.config.panels.conditions.width,
                                      self.config.panels.icon.width)
        self.add_viewport('temperature', row3_columns[0])
        self.add_viewport('conditions', row3_columns[1])
        self.add_viewport('icon', row3_columns[2])
        # Message overlays the weather row.
        self.add_viewport('message', rows[2])

    def on_configure_viewports(self):
        """Required call-back to configure named viewports."""
        log.info('Configure main screen viewports.')
        theme_name = self.config.theme
        if not theme_name:
            raise RuntimeError('No theme specified in configuration.')
        theme = self.config.themes[theme_name]
        self.configure_viewport('time',
                                fx=self.config.panels.time.fx,
                                fy=self.config.panels.time.fy,
                                font_name=self.config.fonts.time,
                                font_size=self.config.panels.time.font_size,
                                color=theme.time,
                                bg_color=theme.background,
                                border_color=theme.border,
                                margins=self.config.panels.time.margins)
        self.configure_viewport('date',
                                fx=self.config.panels.date.fx,
                                fy=self.config.panels.date.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.date.font_size,
                                color=theme.date,
                                bg_color=theme.background,
                                border_color=theme.border,
                                margins=self.config.panels.date.margins)
        self.configure_viewport('seconds',
                                fx=self.config.panels.seconds.fx,
                                fy=self.config.panels.seconds.fy,
                                font_name=self.config.fonts.time,
                                font_size=self.config.panels.seconds.font_size,
                                color=theme.seconds,
                                bg_color=theme.background,
                                border_color=theme.border,
                                margins=self.config.panels.seconds.margins)
        self.configure_viewport('temperature',
                                fx=self.config.panels.temperature.fx,
                                fy=self.config.panels.temperature.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.temperature.font_size,
                                color=theme.temperature,
                                bg_color=theme.background,
                                border_color=theme.border,
                                margins=self.config.panels.temperature.margins)
        self.configure_viewport('conditions',
                                fx=self.config.panels.conditions.fx,
                                fy=self.config.panels.conditions.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.conditions.font_size,
                                color=theme.conditions,
                                bg_color=theme.background,
                                border_color=theme.border,
                                margins=self.config.panels.conditions.margins)
        self.configure_viewport('icon',
                                fx=self.config.panels.icon.fx,
                                fy=self.config.panels.icon.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.icon.font_size,
                                bg_color=theme.background,
                                border_color=theme.icon_border or theme.border,
                                margins=self.config.panels.icon.margins)
        self.configure_viewport('message',
                                fx=self.config.panels.message.fx,
                                fy=self.config.panels.message.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.message.font_size,
                                color=theme.message,
                                bg_color=theme.background,
                                border_color=theme.border,
                                margins=self.config.panels.message.margins)

    def on_create_panels(self):
        """Required call-back to create panels assigned to named viewports."""
        log.info('Create main screen panels.')
        self.set_panel('time',
                       TimePanel(self.config.panels.time.format,
                                 ghost_lcd=self.config.ghost_lcd))
        self.set_panel('seconds',
                       TimePanel(self.config.panels.seconds.format,
                                 ghost_lcd=self.config.ghost_lcd))
        self.set_panel('date',
                       TimePanel(self.config.panels.date.format))
        self.set_panel('temperature',
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.panels.temperature.format,
                                    self.config.domain,
                                    self.config.email,
                                    self.config.metric))
        self.set_panel('conditions',
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.panels.conditions.format,
                                    self.config.domain,
                                    self.config.email))
        self.set_panel('icon',
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.panels.icon.format,
                                    self.config.domain,
                                    self.config.email))
        self.set_panel('message',
                       MessagePanel())
