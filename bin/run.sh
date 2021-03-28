#!/usr/bin/sh

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

# This is the easiest way to run rpi-clock. It makes sure NTP has finished
# synchronizing the time. It automatically uses sudo to run as root, as needed.
# It creates a .pid file to make stopping it, e.g. using kill.sh, simpler. It
# runs in the background and captures all output to the .log file.
#
# To enable this program at startup add something like the following line to
# /etc/rc.local:
#
#    sh /home/pi/rpi-clock/bin/run.sh
#
# Change the path as needed for your rpi-clock installation folder.
#
# If it fails to start check the text console where system messages are
# displayed. You may see problems like NTP synchronization failures. E.g. it may
# have given up waiting for NTP synchronization to complete.

# shellcheck disable=SC2046 disable=SC2209

_wait_for_ntp() {
  echo "Checking for NTP synchronization..."
  for idx in $(seq 10); do
    {  timedatectl show | grep -q 'NTPSynchronized=yes'; } && return
    echo "Waiting for NTP synchronization to complete [$idx]..."
    sleep 20
  done
  echo "ERROR: Gave up waiting for NTP synchronization."
  exit 1
}

_run() {
  app_dir=$(dirname $(dirname "$0"))
  log_dir="$app_dir/log"
  test -d "$log_dir" || mkdir "$log_dir"
  run_dir="$app_dir/run"
  test -d "run_dir" || mkdir "$run_dir"
  script="$app_dir/rpi-clock.py"
  log_file="$log_dir/rpi-clock.log"
  pid_file="$run_dir/rpi-clock.pid"
  rm_cmd=rm
  python_cmd=python3
  cd "$app_dir" || exit 1
  if [ $(id -u) -ne 0 ]; then
    rm_cmd="sudo rm"
    python_cmd="sudo python3"
  fi
  _wait_for_ntp
  test -f "$pid_file" && ${rm_cmd} -f "$pid_file"
  test -f "$log_file" && ${rm_cmd} -f "$log_file"
  touch "$pid_file" "$log_file"
  if [ $(id -u) -eq 0 ]; then
    chown pi:pi "$pid_file" "$log_file"
    { ${python_cmd} "$script"; } >> "$log_file" 2>&1 &
    echo $! >>"$pid_file"
  else
    { ${python_cmd} "$script"; } | tee -a "$log_file" 2>&1
  fi
}

_run
