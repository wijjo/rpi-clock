#!/bin/sh
_app_dir=`dirname $0`
_log_file=$_app_dir/rpi-clock.log
tail -F $_log_file
