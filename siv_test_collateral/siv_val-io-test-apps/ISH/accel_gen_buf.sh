# -------------- IIO buffer ----------------------------
# !/bin/bash

# modprobe only needed before alpha2 ISH driver
# sh accel_name_mod.sh
sleep 1s

d=-1;
while [ $d -ne 11 ]
do
echo $((d++))

# device 0 - 11
cd /iiotest
./generic_buffer_$d -n accel_3d -c 3 &

echo " "
sleep 2s

name2=`cat /sys/bus/iio/devices/iio:device$d/name`
exp_string="accel_3d"
if [[ "$exp_string" == $name2 ]]
then

# to read 3 times
a=0;
while [ $a -ne 3 ]
do
echo $((a++))

# to read real-time data
# cat in_accel_x_raw in_accel_y_raw in_accel_z_raw
x=`cat /sys/bus/iio/devices/iio:device$d/in_accel_x_raw`
y=`cat /sys/bus/iio/devices/iio:device$d/in_accel_y_raw`
z=`cat /sys/bus/iio/devices/iio:device$d/in_accel_z_raw`

echo "x$d = $x"
echo "y$d = $y"
echo "z$d = $z"

x_check=$(echo "($x)" | bc)
y_check=$(echo "($y)" | bc)
z_check=$(echo "($z)" | bc)

# To make sure the x,y,z value received are not all zero.	
zero=0;
null= ;

if [[ $x_check != "$zero" && $x_check != "$null" ]]; then
echo "pass"
fi
if [[ $y_check != "$zero" && $y_check != "$null" ]]; then
echo "pass"
fi
if [[ $z_check != "$zero" && $z_check != "$null" ]]; then
echo "pass"
fi

done
fi
done

echo ""
sleep 1s
exit

