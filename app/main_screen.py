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
        row1_columns = rows[0].hsplit(self.config.panels.time.width,
                                      self.config.panels.seconds.width)
        self.add_viewport('time', row1_columns[0])
        self.add_viewport('seconds', row1_columns[1])
        self.add_viewport('date', rows[1])
        self.add_viewport('weather', rows[2])
        self.add_viewport('message', rows[3])

    # noinspection DuplicatedCode
    def on_configure_viewports(self):
        log.info('Configure main screen viewports.')
        self.configure_viewport('time',
                                fx=self.config.panels.time.fx,
                                fy=self.config.panels.time.fy,
                                font_name=self.config.fonts.time,
                                font_size=self.config.panels.time.font_size,
                                color=self.config.panels.time.color,
                                bg_color=self.config.panels.time.bg_color,
                                margins=self.config.panels.time.margins)
        self.configure_viewport('seconds',
                                fx=self.config.panels.seconds.fx,
                                fy=self.config.panels.seconds.fy,
                                font_name=self.config.fonts.time,
                                font_size=self.config.panels.seconds.font_size,
                                color=self.config.panels.seconds.color,
                                bg_color=self.config.panels.seconds.bg_color,
                                margins=self.config.panels.seconds.margins)
        self.configure_viewport('date',
                                fx=self.config.panels.date.fx,
                                fy=self.config.panels.date.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.date.font_size,
                                color=self.config.panels.date.color,
                                bg_color=self.config.panels.date.bg_color,
                                margins=self.config.panels.date.margins)
        self.configure_viewport('weather',
                                fx=self.config.panels.weather.fx,
                                fy=self.config.panels.weather.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.weather.font_size,
                                color=self.config.panels.weather.color,
                                bg_color=self.config.panels.weather.bg_color,
                                margins=self.config.panels.weather.margins)
        self.configure_viewport('message',
                                fx=self.config.panels.message.fx,
                                fy=self.config.panels.message.fy,
                                font_name=self.config.fonts.text,
                                font_size=self.config.panels.message.font_size,
                                color=self.config.panels.message.color,
                                bg_color=self.config.panels.message.bg_color,
                                margins=self.config.panels.message.margins)

    def on_create_panels(self):
        user_agent = f'({self.config.domain}, {self.config.email})'
        log.info('Create main screen panels.')
        self.set_panel('time',
                       TimePanel(self.config.panels.time.format))
        self.set_panel('seconds',
                       TimePanel(self.config.panels.seconds.format))
        self.set_panel('date',
                       TimePanel(self.config.panels.date.format))
        self.set_panel('weather',
                       WeatherPanel(self.config.latitude,
                                    self.config.longitude,
                                    self.config.panels.weather.format,
                                    user_agent=user_agent))
        self.set_panel('message',
                       MessagePanel())

    def on_button1(self):
        self.event_manager.send('trigger', 'screen', 'main')

    def on_button2(self):
        self.message('button2', duration=5)
