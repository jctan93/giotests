#!/bin/sh

a=-1;
while [ $a -ne 13 ]
do 
echo $((a++))
x_1=`cat /sys/bus/iio/devices/iio:device$a/in_accel_scale`
echo "/sys/bus/iio/devices/iio:device$a/in_accel_scale=$x_1"

zero=0.000009;

if [ "$zero" == "$x_1" ]; then
echo "pass"
fi

done 
exit 