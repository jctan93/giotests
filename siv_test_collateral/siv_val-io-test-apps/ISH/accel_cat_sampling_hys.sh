#!/bin/sh

d=-1;
while [ $d -ne 13 ]
do
echo $((d++))
dev_name=`cat /sys/bus/iio/devices/iio:device$d/name`
echo "/sys/bus/iio/devices/iio:device$d/name=$dev_name"

# v=0;
# while [ $v -ne 15 ]
# do
# echo $((v++))

Initial=1
Step=0.5
Count=20
for (( i=0; i < $Count; i++ ))
do
v=$(echo "$Initial + ( $Step * $i )" | bc)
echo $v

echo $v > /sys/bus/iio/devices/iio:device$d/in_accel_sampling_frequency
echo "echo $v > /sys/bus/iio/devices/iio:device$d/in_accel_sampling_frequency"
sampling=`cat /sys/bus/iio/devices/iio:device$d/in_accel_sampling_frequency`
echo "cat /sys/bus/iio/devices/iio:device$d/in_accel_sampling_frequency= $sampling"

echo $v > /sys/bus/iio/devices/iio:device$d/in_accel_hysteresis
echo "echo $v > /sys/bus/iio/devices/iio:device$d/in_accel_hysteresis"
hysteresis=`cat /sys/bus/iio/devices/iio:device$d/in_accel_hysteresis`
echo "cat /sys/bus/iio/devices/iio:device$d/in_accel_hysteresis= $hysteresis"

done
done

exit

