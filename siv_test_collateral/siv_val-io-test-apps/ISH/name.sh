# -------------- Raw Data Test Script ----------------------------
# This test script is used to validate IIO path with reading raw data of 
# accelerometer (x, y and z axis) through IIO path with BTX Yocto Linux
# BKC image on CHT/MH board with ISH driver patches.
#
# To execute this script, run command sh accel_read.sh after you have
# position the Sensor Orientation.
# ---------------------------------------------------------------------------


#!/bin/bash

## check
# modprobe hid-heci-ish

# sleep 1s

dev0=`cat /sys/bus/iio/devices/iio:device0/name`
echo "/sys/bus/iio/devices/iio:device0/name=$dev0"
dev1=`cat /sys/bus/iio/devices/iio:device1/name`
echo "/sys/bus/iio/devices/iio:device1/name=$dev1"
dev2=`cat /sys/bus/iio/devices/iio:device2/name`
echo "/sys/bus/iio/devices/iio:device2/name=$dev2"
dev3=`cat /sys/bus/iio/devices/iio:device3/name`
echo "/sys/bus/iio/devices/iio:device3/name=$dev3"
dev4=`cat /sys/bus/iio/devices/iio:device4/name`
echo "/sys/bus/iio/devices/iio:device4/name=$dev4"
dev5=`cat /sys/bus/iio/devices/iio:device5/name`
echo "/sys/bus/iio/devices/iio:device5/name=$dev5"
dev6=`cat /sys/bus/iio/devices/iio:device6/name`
echo "/sys/bus/iio/devices/iio:device6/name=$dev6"
dev7=`cat /sys/bus/iio/devices/iio:device7/name`
echo "/sys/bus/iio/devices/iio:device7/name=$dev7"
dev8=`cat /sys/bus/iio/devices/iio:device8/name`
echo "/sys/bus/iio/devices/iio:device8/name=$dev8"
dev9=`cat /sys/bus/iio/devices/iio:device9/name`
echo "/sys/bus/iio/devices/iio:device9/name=$dev9"
dev10=`cat /sys/bus/iio/devices/iio:device10/name`
echo "/sys/bus/iio/devices/iio:device10/name=$dev10"
dev11=`cat /sys/bus/iio/devices/iio:device11/name`
echo "/sys/bus/iio/devices/iio:device11/name=$dev11"
dev12=`cat /sys/bus/iio/devices/iio:device12/name`
echo "/sys/bus/iio/devices/iio:device12/name=$dev12"
dev13=`cat /sys/bus/iio/devices/iio:device13/name`
echo "/sys/bus/iio/devices/iio:device13/name=$dev13"

#pass

exit 1