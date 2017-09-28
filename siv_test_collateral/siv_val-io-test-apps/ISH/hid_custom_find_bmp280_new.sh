# -------------- HID Custom Sensor Test Script ----------------------------
# This test script is used capture the sensor model and read x,y,z.
# 0044:8086:22D8.000X, HID-SENSOR-2000e1.X.auto:
# This X number is not a fixed number, need to change accordingly 
# ISH custom sensors shall expose themselves as HID custom sensors and follow the HID Sensor Usages Spec
# ---------------------------------------------------------------------------
#!/bin/bash

## check
# bosch="66 0 79 0 83 0 67 0 72 0 0 0 0 0 0 0"
bmp280="98 10 91 12 50 56 48"

# dir_ar=($(ls /sys/bus/iio/devices/))
dir_ar=($(find /sys/bus/hid/devices/0044:8086:22D8.000*/HID-SENSOR-2000e*.*.auto/feature-*-*/))

for dir in ${dir_ar[@]}
do
    value=`cat ${dir}feature-*-*-value`
		echo "value= $value"
		echo "${dir}feature-*-*-value"
		
		bmp280="98 10 91 12 50 56 48"
		if [[ $bmp280 == *"$value"* ]]
	then
		echo "1.0 bmp280" 
	fi

done

exit 1


	