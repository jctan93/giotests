#!/bin/sh

g=-1;
while [ $g -ne 13 ]
do
echo $((g++))

name0=`cat /sys/bus/iio/devices/iio:device$g/name`
echo "/sys/bus/iio/devices/iio:device$g/name=$name0"

dev1=`cat /sys/bus/iio/devices/iio:device$g/in_pressure_raw`
echo "/sys/bus/iio/devices/iio:device$g/in_pressure_raw=$dev1"

zero=0;
devname=press;
if [ "$zero" != "$dev1" ] && [ "$devname" == "$name0" ]; then
echo "pass"
fi

dev2=`cat /sys/bus/iio/devices/iio:device$g/in_pressure_raw`
echo "/sys/bus/iio/devices/iio:device$g/in_pressure_raw=$dev2"

if [ "$zero" != "$dev2" ] && [ "$devname" == "$name0" ]; then
echo "pass"
fi

dev3=`cat /sys/bus/iio/devices/iio:device$g/in_pressure_raw`
echo "/sys/bus/iio/devices/iio:device$g/in_pressure_raw=$dev3"

if [ "$zero" != "$dev3" ] && [ "$devname" == "$name0" ]; then
echo "pass"
fi

done

exit
