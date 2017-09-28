#!/bin/bash

pkill -SIGTERM -x aplay
pkill -SIGTERM -x arecord
pkill -SIGTERM -x top
pkill -SIGTERM -x LPE_script.sh
pkill -SIGTERM -x LPE_stress.sh
kill_id=`ps ax | grep -v grep | grep 'dmesg_logger.sh' | awk '{print$1}'`
kill -SIGTERM $kill_id
ls /root/ | grep SWAP_LOG_TEMP > /dev/null
if [ $? -eq 0 ]; then
    rm -f /root/SWAP_LOG_TEMP
fi
