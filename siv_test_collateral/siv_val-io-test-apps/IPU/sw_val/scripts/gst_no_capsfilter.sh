#!/bin/bash

RESULT="PASS"
DESCRIPTION=""
CASE_NAME=$1

export GST_DEBUG=*:5
export GST_DEBUG_FILE="${CASE_NAME}_gst_debug.log"
LOG_FILE="${CASE_NAME}_gst_messages.log"

#Run test
gst-launch-1.0 -m icamerasrc > $LOG_FILE

retval=$?
if [ $retval -ne 0 ];then
    RESULT="FAIL"
    DESCRIPTION="Error.Please refer to file ${LOG_FILE}"
fi

echo "Test Case: $CASE_NAME"
echo "Result: $RESULT"
echo "Description: $DESCRIPTION"
