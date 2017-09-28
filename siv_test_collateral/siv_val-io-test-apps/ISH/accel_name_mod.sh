# -------------- modprobe ISH driver ----------------------------
#!/bin/bash

## check

dir_ar=($(find /sys/bus/iio/devices/iio\:device*/name))
for dir in ${dir_ar[@]}
do
	name1=`cat ${dir}`
	echo "${dir}= $name1"
	
	exp_string="accel_3d"
    if [ "$name1" == "$exp_string" ]; then
        echo "pass"
	fi

done 


exit

