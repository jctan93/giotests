# -------------- modprobe ISH driver ----------------------------
#!/bin/bash

ls -l /sys/bus/iio/devices/ | grep HID-SENSOR-200073> /iiotest/log_hid_200073
hid_200073= `cat /iiotest/log_hid_200073`

exp_string="200073"
	if [[ $exp_string == *"$hid_200073"* ]]
	then
		cat /iiotest/log_hid_200073
		echo "This is HID-SENSOR-200073 device"
        echo "pass"
	fi

d=-1;
while [ $d -ne 13 ]
do
echo $((d++))
	
name2=`cat /sys/bus/iio/devices/iio:device$d/name`
exp_string2="accel_3d"
if [[ "$exp_string2" == $name2 ]]
then
	echo "device $d is accel_3d - pass"
fi

done

exit 