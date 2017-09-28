# -------------- modprobe ISH driver ----------------------------
#!/bin/bash

ls -l /sys/bus/iio/devices/ | grep HID-SENSOR-200041> /iiotest/log_hid_200041
hid_200041= `cat /iiotest/log_hid_200041`

exp_string="200041"
	if [[ $exp_string == *"$hid_200041"* ]]
	then
		cat /iiotest/log_hid_200041
		echo "This is HID-SENSOR-200041 device"
        echo "pass"
	fi

d=-1;
while [ $d -ne 13 ]
do
echo $((d++))
	
name2=`cat /sys/bus/iio/devices/iio:device$d/name`
exp_string2="als"
if [[ "$exp_string2" == $name2 ]]
then
	echo "device $d is $name2 - pass"
fi

done

exit 