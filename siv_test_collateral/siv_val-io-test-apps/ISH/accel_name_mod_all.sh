# -------------- modprobe ISH driver ----------------------------
#!/bin/bash

## script 1
sleep 1s
modprobe hid-heci-ish
sleep 1s

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
sleep 10s

# script 2
sleep 10s
lspci | grep 5aa2 > /iiotest/log_pci
pci_1= `cat /iiotest/log_pci`

exp_string="5aa2"
	if [[ $exp_string == *"$pci_1"* ]]
	then
        echo "pass"
	fi

sleep 10s


# script 3
sleep 10s

ls -l /sys/bus/iio/devices | grep 200073 > log_hid
log2= `cat log_hid`
exp_str="HID-SENSOR-200073"
if [[ $exp_str == *"$log2"* ]]
then 
echo "pass"
fi

sleep 10s