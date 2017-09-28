# -------------- Raw Data (Convert to g) Test Script ----------------------------
# This test script is used to validate IIO path with reading raw data of 
# accelerometer (x, y and z axis) through IIO path with BTX Yocto Linux
# BKC image on CHT/MH board with ISH driver.
#
# To execute this script, run command sh accel_read_xyz_stress.sh after you have
# position the Sensor Orientation.
# ---------------------------------------------------------------------------
#!/bin/sh

dev0=`cat /sys/bus/iio/devices/iio:device0/name`
echo "/sys/bus/iio/devices/iio:device0/name=$dev0"
dev1=`cat /sys/bus/iio/devices/iio:device1/name`
echo "/sys/bus/iio/devices/iio:device1/name=$dev1"
dev2=`cat /sys/bus/iio/devices/iio:device2/name`
echo "/sys/bus/iio/devices/iio:device2/name=$dev2"
dev3=`cat /sys/bus/iio/devices/iio:device3/name`
echo "/sys/bus/iio/devices/iio:device3/name=$dev3"
dev4=`cat /sys/bus/iio/devices/iio:device4/name`
echo "/sys/bus/iio/devices/iio:device4/name=$dev4"
dev5=`cat /sys/bus/iio/devices/iio:device5/name`
echo "/sys/bus/iio/devices/iio:device5/name=$dev5"
dev6=`cat /sys/bus/iio/devices/iio:device6/name`
echo "/sys/bus/iio/devices/iio:device6/name=$dev6"
dev7=`cat /sys/bus/iio/devices/iio:device7/name`
echo "/sys/bus/iio/devices/iio:device7/name=$dev7"
dev8=`cat /sys/bus/iio/devices/iio:device8/name`
echo "/sys/bus/iio/devices/iio:device8/name=$dev8"
dev9=`cat /sys/bus/iio/devices/iio:device9/name`
echo "/sys/bus/iio/devices/iio:device9/name=$dev9"
dev10=`cat /sys/bus/iio/devices/iio:device10/name`
echo "/sys/bus/iio/devices/iio:device10/name=$dev10"
dev11=`cat /sys/bus/iio/devices/iio:device11/name`
echo "/sys/bus/iio/devices/iio:device11/name=$dev11"
dev12=`cat /sys/bus/iio/devices/iio:device12/name`
echo "/sys/bus/iio/devices/iio:device12/name=$dev12"
dev13=`cat /sys/bus/iio/devices/iio:device13/name`
echo "/sys/bus/iio/devices/iio:device13/name=$dev13"

dir_ar=($(find /sys/bus/iio/devices/iio\:device*/in_pressure_raw))

for dir in ${dir_ar[@]}
do

f=0;
while [ $f -ne 5 ]
do
echo $((f++))
	value=`cat ${dir}`
	# echo "1.0 ${dir}= $value"
	
 
scale3=1.000000;

	# value_g=$(echo "(($value*$scale3))" | bc)
	value_g=$(echo "(($value))" | bc)
	
	round_g=$(printf "%.0f\n" $value_g)
	# echo "${dir} = $value_g g "
	echo "${dir}= $round_g  (raw) "

	value_g_check=$(echo "($value_g)" | bc)
	zero=0;

# to make sure the x,y,z value received is not all zero.	
	
	if [ "$zero" != "$value_g_check" ]; then
	echo "pass"
	fi
done

done 
exit
