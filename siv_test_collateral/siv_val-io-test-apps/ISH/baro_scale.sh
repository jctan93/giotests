#!/bin/sh

a=-1;
while [ $a -ne 13 ]
do 
echo $((a++))
x_1=`cat /sys/bus/iio/devices/iio:device$a/in_pressure_scale`
echo "/sys/bus/iio/devices/iio:device$a/in_pressure_scale=$x_1"

one=1.000000;

if [ "$one" == "$x_1" ]; then
echo "pass"
fi

done 
exit 