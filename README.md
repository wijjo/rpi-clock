# rpi-clock

A simple clock for Raspberry Pi and Adafruit PiTFT display and buttons.

It is designed as a "batteries-included" kit to make it easy to build Raspberry
Pi status monitors, including clocks. It works with an Adafruit PiTFT display,
but should be easily adapted to others, and also to other GPIO input devices.

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
* The application is fully-specified in the "config.json" file. I.e. no 
  application-specific Python code is needed.

## Development toolkit features

### Source code

* Fully-typed Python 3 code that 100% passes PyCharm code inspection.
* Fully-documented public classes, functions, and methods.
* Sample configuration file.
* Limited, but useful free font resource library.
* No external dependencies beyond Python 3, PyGame, and framebuffer/GPIO device support.
* Simple management scripts (run.sh/kill.sh/tail.sh).

### Utility scripts

The `bin` folder has the following utility scripts.

* `build.py` - build and deploy distribution using `rsync`.
* `kill.sh` - kill process started by `run.sh` script.
* `run.sh` - run tracked and logged `rpi-clock.py` instance.
* `tail.sh` - tail the log produced by the `run.sh` script running instance.
  
### Component package architecture

The `rpiclock` library has been broken up into the packages described in the
following subsections. Their inter-dependencies are documented in
`doc/package-dependencies.md`.

#### controller

The controller is the top level component that pulls together the configuration
and application pieces, and then runs the application main loop.

A developer can freely decide to build an application in Python code or use the
completely configuration-driven support implemented by `configured_main` and
`configured_screen`.

#### drivers

Hardware and display support is broken into abstract and implementation classes.
The only current implementations support the Raspberry Pi hardware platform and
PyGame for display.

#### events

This package provides the event production and handling framework. It includes
an event producers registry from which outside handlers can subscribe to
generated runtime events.

#### panels

Panels provide registered implementations that talk to the outside world and can
display information in screen viewports (described in the `screen` subsection).

#### screen

The `screen` package is the logical front end to the display. It divides logical
screens into rectangles called `viewports`. Viewports determine how panels
appear to the user. They hold and apply display attributes, like font, text
size, alignment, and margins.

#### utility

This package has a mixture of independent functions and classes that support a
variety of general-purpose capabilities. They depend on no other packages.

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
sudo pip3 install --upgrade -r requirements-rpi.txt
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

## Running the clock at boot time.

Add the following line to `/etc/rc.local`, e.g. if this project is installed to
`/home/pi/rpi-clock`.

```shell
sh /home/pi/rpi-clock/run.sh
```
