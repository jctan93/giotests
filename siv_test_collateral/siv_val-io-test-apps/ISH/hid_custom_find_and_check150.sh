# -------------- HID Custom Sensor Test Script ----------------------------
# This test script is used capture the sensor model and read x,y,z.
# 0044:8086:22D8.000X, HID-SENSOR-2000e1.X.auto:
# This X number is not a fixed number, need to change accordingly 
# ISH custom sensors shall expose themselves as HID custom sensors and follow the HID Sensor Usages Spec
# ---------------------------------------------------------------------------
#!/bin/bash

sh hid_custom_find_bmc150.sh > /iiotest/log_custom

log_custom_1= `cat /iiotest/log_custom`

exp_string="66 0 77 0 67 0 49 0 53 0 48 0 32 0 83 0 101 0 110 0 115 0 111"
	if [[ $exp_string == *"$log_custom_1"* ]]
	then
		echo "custom sensor - bmc150" 
        echo "1.0 pass"
		# sh hid_custom_bmc150.sh > /iiotest/log_check
		# cat /iiotest/log_check
	fi

# check for 5 devices
f=-1;
while [ $f -ne 6 ]
do 
echo $((f++))

d=-1;
while [ $d -ne 9 ]
do
echo $((d++))

dir2=($(echo "/sys/bus/hid/devices/0044:8086:22D8.000$f/HID-SENSOR-2000e1.$d.auto/"))
# dir2=($(echo "/sys/bus/hid/devices/0044:8086:22D8.0002/HID-SENSOR-2000e1.1.auto/"))
# dir2=($(echo "/sys/bus/hid/devices/0044:8086:22D8.0002/HID-SENSOR-2000e1.3.auto/"))

echo "$dir2"

bmc150_accel="66 0 77 0 67 0 49 0 53 0 48 0 32 0 83 0 101 0 110 0 115 0 111"
val_accel_150=`cat ${dir2}feature-8-200306/feature-8-200306-value`

if [[ $val_accel_150 == *"$bmc150_accel"* ]]
then
	echo "-- BMC150 Sensor --";
	echo "$val_accel_150";
fi

en_sensor=`cat ${dir2}enable_sensor`
echo "1. en_sensor= $en_sensor"

zero=0;
if [ "$zero" == "$en_sensor" ]; then
echo 1 > /sys/bus/hid/devices/0044:8086:22D8.000$f/HID-SENSOR-2000e1.$d.auto/enable_sensor
# echo 1 > /sys/bus/hid/devices/0044:8086:22D8.0002/HID-SENSOR-2000e1.3.auto/enable_sensor
echo "2. en_sensor= $en_sensor"
fi
echo "3. en_sensor= $en_sensor"

g=0;
while [ $g -ne 3 ]
do
echo $((g++))

# x-axis
# accel_x=`cat ${dir2}input-4-200544/input-4-200544-value`
accel_x=`cat ${dir2}input-5-200544/input-5-200544-value`
echo "x = $accel_x"
# y-axis
# accel_y=`cat ${dir2}input-5-200545/input-5-200545-value`
accel_y=`cat ${dir2}input-6-200545/input-6-200545-value`

echo "y = $accel_y"
# z-axis
# accel_z=`cat ${dir2}input-6-200546/input-6-200546-value`
accel_z=`cat ${dir2}input-7-200546/input-7-200546-value`
echo "z = $accel_z"

# unit is exponential -6
# unit_x=`cat ${dir2}input-4-200544/input-4-200544-unit-expo`
unit_x=`cat ${dir2}input-5-200544/input-5-200544-unit-expo`
echo "unit expo $unit_x"
# echo "$accel_x*10^-06" | bc -l
data_x=$(echo "($accel_x*10^-06)" | bc -l)
# echo "$data_x "
round_x=$(printf "%2.4f\n" $data_x)
echo "x1 = $round_x   "

data_y=$(echo "($accel_y*10^-06)" | bc -l)
round_y=$(printf "%2.4f\n" $data_y)
echo "y1 = $round_y   "

data_z=$(echo "($accel_z*10^-06)" | bc -l)
round_z=$(printf "%2.4f\n" $data_z)
echo "z1 = $round_z   "

zero=0;
one=1;
if [ "$zero" != "$accel_x" ] && [ "$en_sensor" == "$one" ]; then
echo "pass"
fi

if [ "$zero" != "$accel_y" ] && [ "$en_sensor" == "$one" ]; then
echo "pass"
fi

if [ "$zero" != "$accel_z" ] && [ "$en_sensor" == "$one" ]; then
echo "pass"
fi

done

done

done
	
exit


	
