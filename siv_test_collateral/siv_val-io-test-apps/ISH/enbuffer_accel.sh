#!/bin/sh

echo 1 > /sys/bus/iio/devices/iio:device4/scan_elements/in_accel_x_en
echo 1 > /sys/bus/iio/devices/iio:device4/scan_elements/in_accel_y_en
echo 1 > /sys/bus/iio/devices/iio:device4/scan_elements/in_accel_z_en
echo 1 > /sys/bus/iio/devices/iio:device4/buffer/enable

cat /sys/bus/iio/devices/iio:device4/buffer/enable

dmesg | tail -n 40



exit
