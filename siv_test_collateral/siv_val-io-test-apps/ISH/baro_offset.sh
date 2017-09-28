#!/bin/sh

a=-1;
while [ $a -ne 13 ]
do 
echo $((a++))
offset_1=`cat /sys/bus/iio/devices/iio:device$a/in_pressure_offset`
echo "/sys/bus/iio/devices/iio:device$a/in_pressure_offset=$offset_1"

zero=0;
one=1;
if [ "$zero" == "$offset_1" ]; then
echo "pass"
fi

done 
exit 