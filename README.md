# rpi-clock

A simple clock for Raspberry Pi and Adafruit PiTFT display and buttons.

It is designed as a "batteries-included" kit to make it easy to build Raspberry
Pi status monitors, including clocks. It works with an Adafruit PiTFT display,
but should be easily adapted to others, and also to other GPIO input devices.

Please note that it is not limited to the PiTFT as a framebuffer device. Any
similar device should be configurable. It just has not been tested.

It is largely configuration data-driven. See examples/config.json.

You can mix and match the included panel classes, or your own, and assign them
to display "viewports" with customizable placement, fonts, colors, etc.

Utility modules are provided for invoking and receiving data from Web APIs, 
events, timers.

It also includes a set of free fonts to get you started with text display.

These instructions will probably need elaboration, but for now it is the best-
recollection of what needs to happen to take advantage of this project.

## Clock features (out of the box)

* Large digital time display with seconds.
* Periodically-updated NOAA weather data, including temperature and conditions text/image.
* PiTFT button 3 shuts quits application.
* Font/color/position customization in config.json.

## Development toolkit features

### Source code

* Fully-typed Python 3 code that 100% passes PyCharm code inspection.
* Fully-documented public classes, functions, and methods.
* Sample configuration file.
* Limited, but useful free font resource library.
* No external dependencies beyond Python 3, PyGame, and framebuffer/GPIO device support.
* Simple management scripts (run.sh/kill.sh/tail.sh).
  
### Model/view/controller (MVC) architecture

Provides the following components:

#### Model: data sources

Configurable data sources support JSON and file downloads with automatic caching
and expiration timing.

#### View: viewports and screens

Viewports are logical display regions with assigned fonts, colors, and margins.

Screens are logical full-screen pages with their own assigned viewports.

#### Controller: panels, events, and controller

Panels are assigned to viewports. They pull in external data and format screen output.

Included panels support text, time, and weather display in various formats.

Events are implemented as producers and handlers. Producers map external triggers, 
like time and hardware button events, to logical events. Logical events invoke 
handler functions.

Included event producers support GPIO button, tick, timer, and programmatic trigger events.

There is a single controller that provides the main loop and initializes and manages
viewports, panels, and events.

## Licensing

For now this uses a GPL license. At a high level it makes the source code freely
available, but only if the source code remains open. The author is willing to consider
alternatives if there is a demand.

**The above loose statement should not be interpreted as binding license 
terms. Please read the license text itself (in COPYING).**

# Setup

These are recorded from memory, and may be incomplete. It does cover most of what
needs to happen.

## Basic development requirements.

```
sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev
```

## PiTFT development requirements.

```
sudo apt-get install python3-pygame
sudo pip3 install --upgrade adafruit-python-shell click==7.0
sudo pip3 install RPi.GPIO
git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
cd Raspberry-Pi-Installer-Scripts
sudo python3 adafruit-pitft.py
```

# Using the default clock application

Copy `examples/config.json` to the root folder. Edit the file and change JSON
elements like geographical coordinates, domain name, and email address. Note
that the latter 2 pieces of information are needed to satisfy NOAA requirements
for using their weather API.

You can also customize fonts, colors, and panel placement in `config.json`.
Included fonts may be found in the `fonts` folder. They are identified by
lowercase file name without the extension. The `fonts` and `colors` JSON
elements make it easier to centralize and manage these commonly-tweaked items.

The next place to look is the main `rpi-clock.py` script and then 
`app/main-screen.py`. The latter uses configuration data to initialize all the
runtime requirements of the main clock screen, including viewports, panels, and
event handling.

## Running the clock at boot time.

Add the following line to `/etc/rc.local`, e.g. if this project is installed to
`/home/pi/rpi-clock`.

```shell
sh /home/pi/rpi-clock/run.sh
```
