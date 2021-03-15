#!/bin/sh

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
  app_dir=$(dirname "$0")
  script="$app_dir/rpi-clock.py"
  log_file="$app_dir/rpi-clock.log"
  pid_file="$app_dir/rpi-clock.pid"
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
  fi
  { ${python_cmd} "$script"; } >>"$log_file" 2>&1 &
  echo $! >>"$pid_file"
  if [ $(id -u) -ne 0 ]; then
    tail -F "$log_file"
  fi
}

_run
