#!/bin/sh
# shellcheck disable=SC2006 disable=SC2086 disable=SC2024 disable=SC2164
_uid=`id -u`
_app_dir=`dirname $0`
cd $_app_dir
_script=$_app_dir/rpi-clock.py
_log_file=$_app_dir/rpi-clock.log
_pid_file=$_app_dir/rpi-clock.pid
if [ $_uid -eq 0 ]; then
    test -f $_pid_file && rm -f $_pid_file
    test -f $_log_file && rm -f $_log_file
    touch $_pid_file $_log_file
    chown pi:pi $_pid_file $_log_file
    python3 $_script >> $_log_file 2>&1 &
    echo $! >> $_pid_file
else
    test -f $_pid_file && sudo rm -f $_pid_file
    test -f $_log_file && sudo rm -f $_log_file
    touch $_log_file
    sudo python3 $_script >> $_log_file 2>&1 &
    echo $! > $_pid_file
    tail -F $_log_file
fi
