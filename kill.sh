#!/bin/sh
_uid=`id -u`
_app_dir=`dirname $0`
_pid_file=$_app_dir/rpi-clock.pid
if [ -f $_pid_file ]; then
    _pid=`cat $_pid_file`
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
