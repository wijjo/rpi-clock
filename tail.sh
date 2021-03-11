#!/bin/sh
# shellcheck disable=SC2006 disable=SC2086 disable=SC2024
_app_dir=`dirname $0`
_log_file=$_app_dir/rpi-clock.log
tail -F $_log_file
