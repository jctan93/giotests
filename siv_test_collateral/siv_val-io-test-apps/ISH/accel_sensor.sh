#!/bin/sh

g=-1;
while [ $g -ne 13 ]
do
echo $((g++))

dev0=`cat /sys/bus/iio/devices/iio:device$g/name`
echo "/sys/bus/iio/devices/iio:device$g/name=$dev0"

dev1=`cat /sys/bus/iio/devices/iio:device$g/in_accel_x_raw`
echo "/sys/bus/iio/devices/iio:device$g/in_accel_x_raw=$dev1"

zero=0;
if [ "$zero" != "$dev1" ]; then
echo "pass"
fi

dev2=`cat /sys/bus/iio/devices/iio:device$g/in_accel_y_raw`
echo "/sys/bus/iio/devices/iio:device$g/in_accel_y_raw=$dev2"

if [ "$zero" != "$dev2" ]; then
echo "pass"
fi

dev3=`cat /sys/bus/iio/devices/iio:device$g/in_accel_z_raw`
echo "/sys/bus/iio/devices/iio:device$g/in_accel_z_raw=$dev3"

if [ "$zero" != "$dev3" ]; then
echo "pass"
fi

done

exit
