#!/bin/sh

a=-1;
while [ $a -ne 13 ]
do 
echo $((a++))
x_1=`cat /sys/bus/iio/devices/iio:device$a/in_pressure_hysteresis`
echo "/sys/bus/iio/devices/iio:device$a/in_pressure_hysteresis=$x_1"

echo 0.020000 > /sys/bus/iio/devices/iio:device$a/in_pressure_hysteresis
x_2=`cat /sys/bus/iio/devices/iio:device$a/in_pressure_hysteresis`
echo "/sys/bus/iio/devices/iio:device$a/in_pressure_hysteresis=$x_2"

one=0.020000;

if [ "$one" == "$x_2" ]; then
echo "pass"
fi

done 
exit 