# rpi-clock
A simple clock for Raspberry Pi and Adafruit PiTFT display

# Setup

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
