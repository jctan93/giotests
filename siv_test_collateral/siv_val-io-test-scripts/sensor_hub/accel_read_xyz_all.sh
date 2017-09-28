# -------------- Raw Data (Convert to g) Test Script ----------------------------
# This test script is used to validate IIO path with reading raw data of 
# accelerometer (x, y and z axis) through IIO path with BTX Yocto Linux
# BKC image on CHT/MH board with ISH driver.
#
# To execute this script, run command sh accel_read_xyz_stress.sh after you have
# position the Sensor Orientation.
# ---------------------------------------------------------------------------
#!/bin/sh

g=-1;
while [ $g -ne 13 ]
do
echo $((g++))

dev0=`cat /sys/bus/iio/devices/iio:device$g/name`
echo "/sys/bus/iio/devices/iio:device$g/name=$dev0"
done

dir_ar=($(find /sys/bus/iio/devices/iio\:device*/in_accel_*_raw))

for dir in ${dir_ar[@]}
do

f=0;
while [ $f -ne 5 ]
do
echo $((f++))
	value=`cat ${dir}`
	# echo "1.0 ${dir}= $value"
	
# ---------------------------------------------------------------
# The SI derived unit for acceleration is the meter/square second.
# Convert from m/s2 to g-force; 9.80665 m/s2 = 1g
# 1 meter/square second is equal to 0.101971621298 g-unit.
# ---------------------------------------------------------------

scale1=0.0000098 
to_g=0.10197163  

	value_g=$(echo "(($value*$scale1)*$to_g)" | bc)
	round_g=$(printf "%2.4f\n" $value_g)
	# echo "${dir} = $value_g g "
	echo "${dir}= $round_g g "

	value_g_check=$(echo "($value_g)" | bc)
	zero=0;

# to make sure the x,y,z value received is not all zero.	
	
	if [ "$zero" != "$value_g_check" ]; then
	echo "pass"
	fi
done

done 
exit
