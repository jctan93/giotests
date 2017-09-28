#!/bin/bash

RESULT="PASS"
DESCRIPTION=""
CASE_NAME=$1

export GST_DEBUG=*:5
export GST_DEBUG_FILE="${CASE_NAME}_gst_debug.log"

gst-inspect-1.0 icamerasrc | grep "format: YUY2"

retval=$?
if [ $retval -ne 0 ];then
    RESULT="FAIL"
    DESCRIPTION="Error.Please refer to file std log"
fi

echo "Test Case: $CASE_NAME"
echo "Result: $RESULT"
echo "Description: $DESCRIPTION"
