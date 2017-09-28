#!/bin/bash

g=-1;
while [ $g -ne 5 ]
do
echo $((g++))
rmmod intel_ishtp_hid
rmmod intel_ishtp_clients
rmmod intel_ish_ipc
rmmod intel_ishtp
modprobe intel_ish_ipc &
sleep 2

done

dmesg | tail -n 10 > /home/log_loadunload
egrep -i 'dead|fail' /home/log_loadunload > /home/log_loadunload1
words=`wc -l /home/log_loadunload1 | awk '{print $1}'`
echo "$words"
zero=0;
echo "$zero"
log=`cat /home/log_loadunload1`

if [ "$zero" == "$words" ]; then
	echo "pass"
else 
	echo "$log"
	fi
