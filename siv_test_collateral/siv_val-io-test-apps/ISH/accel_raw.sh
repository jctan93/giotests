a=-1;
while [ $a -ne 13 ]
do
    echo $((a++))

	x=0;
	while [ $x -ne 5 ]
	do
    echo $((x++))
	
	raw_1=`cat /sys/bus/iio/devices/iio:device$a/in_accel_x_raw`
    echo "/sys/bus/iio/devices/iio:device$a/in_accel_x_raw=$raw_1"
	
	raw_name=`cat /sys/bus/iio/devices/iio:device$a/name`
	echo "/sys/bus/iio/devices/iio:device$a/name=$raw_name"
	
	zero=0;
	name_value=accel_3d;
	raw_1_check=$(echo "($raw_1)" | bc)
	if [ "$raw_1_check" != "$zero" ] && [ "$raw_name" == "$name_value" ]; then
	echo "pass"
	fi

	done
done

exit
