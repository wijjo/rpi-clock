#!/bin/bash

function _wait_for_ntp() {
  echo "Checking for NTP synchronization..."
  for idx in $(seq 10); do
    {  timedatectl show | grep -q 'NTPSynchronized=yes'; } && return
    echo "Waiting for NTP synchronization to complete [$idx]..."
    sleep 2
  done
  echo "ERROR: Gave up waiting for NTP synchronization."
  exit 1
}

function _run() {
  declare app_dir
  app_dir=$(dirname "$0")
  declare script="$app_dir/rpi-clock.py"
  declare log_file="$app_dir/rpi-clock.log"
  declare pid_file="$app_dir/rpi-clock.pid"
  declare rm_cmd=rm
  declare python_cmd=python3
  cd "$app_dir" || exit 1
  if [[ $(id -u) != 0 ]]; then
    rm_cmd="sudo rm"
    python_cmd="sudo python3"
  fi
  _wait_for_ntp
  test -f "$pid_file" && ${rm_cmd} -f "$pid_file"
  test -f "$log_file" && ${rm_cmd} -f "$log_file"
  touch "$pid_file" "$log_file"
  if [[ $(id -u) == 0 ]]; then
    chown pi:pi "$pid_file" "$log_file"
  fi
  { ${python_cmd} "$script"; } >>"$log_file" 2>&1 &
  echo $! >>"$pid_file"
  if [[ $(id -u) != 0 ]]; then
    tail -F "$log_file"
  fi
}

_run
