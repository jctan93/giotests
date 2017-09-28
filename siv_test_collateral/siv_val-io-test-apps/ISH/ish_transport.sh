# -------------- modprobe ISH driver ----------------------------
#!/bin/bash

## check
ls -l /sys/bus/hid/devices/ > /home/log_transport
transport_1= `cat /home/log_transport` 

cat /home/log_transport

exp_string="22D8"
	if [[ $exp_string == *"$transport_1"* ]]
	then
		echo "This is 22D8 device"
        echo "pass"
	fi
	
exit

