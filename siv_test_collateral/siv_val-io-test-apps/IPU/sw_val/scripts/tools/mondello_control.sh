#!/bin/bash

# MONDELLO_SERVE_IP, get from env"
#. /etc/profile
echo "Mondello server IP address: "$MONDELLO_SERVER_IP
#to deal with dual mondello ips configured but only 1 mondello is used. We default to use the first ip.
if [ ! -z `echo $MONDELLO_SERVER_IP | grep ":"` ];then
    MONDELLO_SERVER_IP=${MONDELLO_SERVER_IP%%:*}
    echo "Selected MONDELLO_SERVER_IP=${MONDELLO_SERVER_IP}"
fi

if [ -z $MONDELLO_SERVER_IP  ]; then
    RESULT="FAIL"
    DESCRIPTION="Error, this case need mondello device, please export MONDELLO_SERVER_IP in device env first or pass ip through arguments."
    echo "Test Case: ${CASE_NAME}"
    echo "Result: $RESULT"
    echo "Description: $DESCRIPTION"
    exit -1
fi

MONDELLO_CONTROL_NEEDED=1
. /home/root/sw_val/scripts/tools/mondello_control_helper.sh
