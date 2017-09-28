#!/bin/sh

a=-1;
while [ $a -ne 13 ]
do 
echo $((a++))
x_1=`cat /sys/bus/iio/devices/iio:device$a/in_accel_sampling_frequency`
echo "/sys/bus/iio/devices/iio:device$a/in_accel_sampling_frequency=$x_1"

echo 1 > /sys/bus/iio/devices/iio:device$a/in_accel_sampling_frequency
x_2=`cat /sys/bus/iio/devices/iio:device$a/in_accel_sampling_frequency`
echo "/sys/bus/iio/devices/iio:device$a/in_accel_sampling_frequency=$x_2"

one=1.000000;

if [ "$one" == "$x_2" ]; then
echo "pass"
fi

done 
exit 