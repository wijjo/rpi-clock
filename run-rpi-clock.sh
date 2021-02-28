#!/bin/bash
scp rpi-clock.py rpi-eth:/tmp/
ssh -t rpi-eth sudo python /tmp/rpi-clock.py
