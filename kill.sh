#!/bin/sh

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

# Kill running rpi-clock application.
# Assumes run.sh was used to generate .pid file.

# shellcheck disable=SC2006 disable=SC2086 disable=SC2024

_uid=$(id -u)
_app_dir=$(dirname $0)
_pid_file=$_app_dir/rpi-clock.pid
if [ -f $_pid_file ]; then
  _pid=$(cat $_pid_file)
  echo "Killing _PID $_pid..."
  if [ $_uid -eq 0 ]; then
    kill $_pid
    rm -fv $_pid_file
  else
    sudo kill $_pid
    sudo rm -fv $_pid_file
  fi
else
  echo "$_pid_file does not exist."
fi
