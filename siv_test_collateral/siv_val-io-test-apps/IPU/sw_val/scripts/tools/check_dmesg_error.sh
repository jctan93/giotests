DMESG_FILTER_OUT=`dmesg | grep -i -E "\[(([0-9]|\.| ){12})\] (crlmodule|intel-ipu4).*(fail|error)"`

if [ -z "$DMESG_FILTER_OUT" ] ; then
    echo "no error/fail info caputred from dmesg"
    exit 0
else
    echo "Warning: error/fail info found in dmesg as following:"
    echo "$DMESG_FILTER_OUT" | while read line; do
        echo "$line"
    done
    exit -1
fi