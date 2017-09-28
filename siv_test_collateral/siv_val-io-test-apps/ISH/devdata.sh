#!/bin/bash

g=-1;
accel_num=0;
while [ $g -ne 6 ]
do
echo $((g++))

dev0=`cat /sys/bus/iio/devices/iio:device$g/name`
echo "/sys/bus/iio/devices/iio:device$g/name=$dev0"
if [ "$dev0" == "accel_3d" ]; then
	accel_num=$g
	fi
done
accel=`expr $accel_num - 1`

echo "Accel_iiodevice = $accel"
cd /sys/bus/iio/devices/iio:device$accel
echo 1 > scan_elements/in_accel_x_en
echo 1 > scan_elements/in_accel_y_en
echo 1 > scan_elements/in_accel_z_en
echo 1 > buffer/enable

cat /dev/iio:device$accel &
sleep 5
kill -9 `pgrep cat`

dmesg | tail -n 30 > /home/log_devdata
egrep -i 'dead|timeout|fail' /home/log_devdata > /home/log_devdata1
words=`wc -l /home/log_devdata1 | awk '{print $1}'`
echo "$words"
zero=0;
echo "$zero"
log1=`cat /home/log_devdata`
log=`cat /home/log_devdata1`

if [ "$zero" == "$words" ]; then
	echo "$log1"
	echo "pass"
else 
	echo "$log"
	fi