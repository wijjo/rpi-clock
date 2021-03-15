from lib import log
from lib.panels.message import MessagePanel
from lib.panels.time import TimePanel
from lib.panels.weather import WeatherPanel
from lib.screen import Screen
from lib.viewport import Viewport


class MainScreen(Screen):

    def on_initialize_events(self):
        self.event_manager.register('button', self.on_button1, 1)
        self.event_manager.register('button', self.on_button2, 2)

    def on_create_viewports(self, outer_viewport: Viewport):
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

    # noinspection DuplicatedCode
    def on_configure_viewports(self):
        log.info('Configure main screen viewports.')
        self.configure_viewport('time',
                                fx=self.config.panels.time.fx,
                                fy=self.config.panels.time.fy,
                                font_name=self.config.fonts.time,
                                font_size=self.config.panels.time.font_size,
                                color=self.config.panels.time.color,
                                bg_color=self.config.panels.time.bg_color or self.config.bg_color,
                                border_color=self.config.panels.time.border_color or self.config.border_color,
                                margins=self.config.panels.time.margins)
        self.configure_viewport('date',
                                fx=self.config.panels.date.fx,
                                fy=self.config.panels.date.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.date.font_size,
                                color=self.config.panels.date.color,
                                bg_color=self.config.panels.date.bg_color or self.config.bg_color,
                                border_color=self.config.panels.date.border_color or self.config.border_color,
                                margins=self.config.panels.date.margins)
        self.configure_viewport('seconds',
                                fx=self.config.panels.seconds.fx,
                                fy=self.config.panels.seconds.fy,
                                font_name=self.config.fonts.time,
                                font_size=self.config.panels.seconds.font_size,
                                color=self.config.panels.seconds.color,
                                bg_color=self.config.panels.seconds.bg_color or self.config.bg_color,
                                border_color=self.config.panels.seconds.border_color or self.config.border_color,
                                margins=self.config.panels.seconds.margins)
        self.configure_viewport('temperature',
                                fx=self.config.panels.temperature.fx,
                                fy=self.config.panels.temperature.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.temperature.font_size,
                                color=self.config.panels.temperature.color,
                                bg_color=self.config.panels.temperature.bg_color or self.config.bg_color,
                                border_color=self.config.panels.temperature.border_color or self.config.border_color,
                                margins=self.config.panels.temperature.margins)
        self.configure_viewport('conditions',
                                fx=self.config.panels.conditions.fx,
                                fy=self.config.panels.conditions.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.conditions.font_size,
                                color=self.config.panels.conditions.color,
                                bg_color=self.config.panels.conditions.bg_color or self.config.bg_color,
                                border_color=self.config.panels.conditions.border_color or self.config.border_color,
                                margins=self.config.panels.conditions.margins)
        self.configure_viewport('icon',
                                fx=self.config.panels.icon.fx,
                                fy=self.config.panels.icon.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.icon.font_size,
                                color=self.config.panels.icon.color,
                                bg_color=self.config.panels.icon.bg_color or self.config.bg_color,
                                border_color=self.config.panels.icon.border_color or self.config.border_color,
                                margins=self.config.panels.icon.margins)
        self.configure_viewport('message',
                                fx=self.config.panels.message.fx,
                                fy=self.config.panels.message.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.message.font_size,
                                color=self.config.panels.message.color,
                                bg_color=self.config.panels.message.bg_color or self.config.bg_color,
                                border_color=self.config.panels.message.border_color or self.config.border_color,
                                margins=self.config.panels.message.margins)

    def on_create_panels(self):
        user_agent = f'({self.config.domain}, {self.config.email})'
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
                                    user_agent=user_agent))
        self.set_panel('conditions',
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.panels.conditions.format,
                                    user_agent=user_agent))
        self.set_panel('icon',
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.panels.icon.format,
                                    user_agent=user_agent))
        self.set_panel('message',
                       MessagePanel())

    def on_button1(self):
        self.event_manager.send('trigger', 'screen', 'main')

    def on_button2(self):
        self.message('button2', duration=5)
