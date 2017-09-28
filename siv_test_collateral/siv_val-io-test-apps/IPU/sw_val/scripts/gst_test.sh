#!/bin/bash

RESULT="PASS"
DESCRIPTION=""

if [ $# -lt 1 ] ; then 
    echo "USAGE: $0 CASE_NAME" 
    exit 1; 
fi

CASE_NAME=$1
SW_VAL_ROOT=/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${SW_VAL_ROOT}/bin

echo 'Parse info from case name'
. ${SW_VAL_ROOT}/scripts/tools/parse_gst_case_name.sh $CASE_NAME

export GST_DEBUG=*:5
export GST_DEBUG_FILE="${CASE_NAME}_gst_debug.log"
LOG_FILE_NAME="${CASE_NAME}_gst_messages.log"

echo "Change to execution dir ${SW_VAL_ROOT}/results"
LOG_DIR=${SW_VAL_ROOT}/results
if [ ! -d $LOG_DIR ]; then
    mkdir $LOG_DIR
fi

cd $LOG_DIR

camrealinput="$cameraInput"
#if [ "$cameraInput" == "mondello" ]; then 
#    if [ "${MONDELLO_FORMAT}" == "rgb24" ]; then
#        camrealinput="mondello-rgb8888"
#    elif [ "${MONDELLO_FORMAT}" == "rgb565" ]; then
#        camrealinput="mondello-rgb565-32bpp"
#    fi
#fi
if [ -z ${camrealinput} ];then
    echo "cameraInput is null! please export cameraInput in dut /etc/profile"
    exit -1
fi

if [ "${CAMERA_NUM}" == "1" ] || [ -z ${CAMERA_NUM} ];then
    . ${SW_VAL_ROOT}/scripts/tools/mondello_control.sh
    if [ ! -z $MONDELLO_FORMAT ]; then
        echo "Get mondello script name according to resolution information ${WIDTH}x${HEIGHT} ${MONDELLO_FORMAT} ${interlace_mode}"
        get_mondello_command_according_res_info ${WIDTH}x${HEIGHT} ${MONDELLO_FORMAT} ${interlace_mode}
    fi

    #run the test
    GST_COMMAND="DISPLAY=:0 gst-launch-1.0 -m icamerasrc printfps=${printfps} num-buffers=${num_buffers} device-name=${camrealinput}"
    if [ ! -z $io_mode ]; then
        GST_COMMAND="${GST_COMMAND} io-mode=${io_mode}"
    fi
    if [ ${interlace_mode} == "true" ] && [ ! -z ${deinterlace_method} ] ; then
        GST_COMMAND="${GST_COMMAND} interlace-mode=alternate deinterlace_method=${deinterlace_method}"
    elif [ ${interlace_mode} == "true" ]; then
        GST_COMMAND="${GST_COMMAND} interlace-mode=alternate"
    fi

    if [ ${camrealinput} == "imx185" ]; then
        pkill xinit
        if [ ${wdr_mode} == "on" ] ; then
            GST_COMMAND="${GST_COMMAND} wdr_mode=on ! \"video/x-raw, format=${FORMAT}, width=${WIDTH}, height=${HEIGHT},tiled=false\" ! ${gstsink} > ${LOG_FILE_NAME}"
        elif [ ${wdr_mode} == "off" ] ; then
	    GST_COMMAND="${GST_COMMAND} wdr_mode=off ! \"video/x-raw, format=${FORMAT}, width=${WIDTH}, height=${HEIGHT},tiled=false\" ! ${gstsink} > ${LOG_FILE_NAME}"
	else 
            GST_COMMAND="${GST_COMMAND} ! \"video/x-raw, format=${FORMAT}, width=${WIDTH}, height=${HEIGHT},tiled=false\" ! ${gstsink} > ${LOG_FILE_NAME}"
        fi
    else
        GST_COMMAND="${GST_COMMAND} ! \"video/x-raw, format=${FORMAT}, width=${WIDTH}, height=${HEIGHT}\" ! ${gstsink} > ${LOG_FILE_NAME}"
    fi

echo "Execute Command: ${GST_COMMAND}"

    if [ $I_TEST_TYPE == "error" ]; then
        eval $GST_COMMAND
        retval=$?
    else
        eval $GST_COMMAND &
        pid=$!
        if [ ! -z $MONDELLO_CONTROL_NEEDED ]; then
            sleep 5
            send_command_to_mondello_server
        fi
        wait $pid
        retval=$?
        if [ ${camrealinput} == "imx185" ]; then
            xinit &
        fi
    fi

elif [ "${CAMERA_NUM}" == "2" ];then
    . ${SW_VAL_ROOT}/scripts/tools/multi_mondello_control.sh ${CAMERA_NUM}
    if [ ! -z $MONDELLO_FORMAT ]; then
        echo "Get mondello script name according to resolution array \"${I_RESOLUTION[*]}\" \"${MONDELLO_FORMAT[*]}\" \"${interlace_mode[*]}\""
        get_mondello_command_arrays_according_res_array I_RESOLUTION[@] MONDELLO_FORMAT[@] interlace_mode[@]
    fi
    GST_COMMAND="DISPLAY=:0 gst-launch-1.0"
    camrealinput2="$cameraInput2"
    if [ -z ${cameraInput2} ];then
        echo "cameraInput2 is null! please export cameraInput2 in dut /etc/profile"
        exit -1
    fi
    
    declare -a camrealinput_a=(${camrealinput} ${camrealinput2})
    
    for((i=`expr ${CAMERA_NUM} - 1`; i>=0; i--))
    do
        GST_COMMAND="${GST_COMMAND} icamerasrc device-name=${camrealinput_a[$i]} printfps=${printfps} num-buffers=${num_buffers} ! video/x-raw,format=${FORMAT[$i]},width=${WIDTH[$i]},height=${HEIGHT[$i]} ! ${gstsink[$i]}"
    done    
    GST_COMMAND="${GST_COMMAND} > ${LOG_FILE_NAME}"
    if [ ! -z $MONDELLO_CONTROL_NEEDED ]; then
        reconnect_to_mondello_servers
        sleep 5
    fi
    echo "Execute Command: ${GST_COMMAND}"
    eval $GST_COMMAND &
    pid=$!
    if [ ! -z $MONDELLO_CONTROL_NEEDED ]; then
        sleep 10
        send_command_arrary_to_mondello_servers
    fi
    wait $pid
    retval=$?
elif [ "${CAMERA_NUM}" == "4" ];then
    if [ "${cameraInput}" == "aggregator" ];then
        . ${SW_VAL_ROOT}/scripts/tools/pixter_control.sh
    fi
    if [ ! -z $PIXTER_CONTROL_NEEDED ]; then
        echo "Get pixter command according to case name ${CASE_NAME}"
        get_pixter_command_by_casename
    fi
    GST_COMMAND="DISPLAY=:0 gst-launch-1.0"
    camrealinput2="$cameraInput2"
    camrealinput3="$cameraInput3"
    camrealinput4="$cameraInput4"
    if [ -z ${cameraInput2} ] || [ -z ${cameraInput3} ] || [ -z ${cameraInput4} ];then
        echo "cameraInput2/3/4 is null! please export cameraInput2/3/4 as aggregator-2/aggregator-3/aggregator-4 for pixter and ov10635-vc-2/ov10635-vc-3/ov10635-vc-4 for 4 real sensors in dut /etc/profile"
        exit -1
    fi
    
    declare -a camrealinput_a=(${camrealinput} ${camrealinput2} ${camrealinput3} ${camrealinput4})
    for((i=0; i<${CAMERA_NUM}; i++))
    do
        GST_COMMAND="${GST_COMMAND} icamerasrc device-name=${camrealinput_a[$i]} num-vc=4 printfps=${printfps} num-buffers=${num_buffers} ! video/x-raw,format=${FORMAT[$i]},width=${WIDTH[$i]},height=${HEIGHT[$i]} ! ${gstsink[$i]}"
    done    
    GST_COMMAND="${GST_COMMAND} > ${LOG_FILE_NAME}"
    if [ ! -z $PIXTER_CONTROL_NEEDED ]; then
        reset_stop_pixter
    fi
    echo "Execute Command: ${GST_COMMAND}"
    eval $GST_COMMAND &
    pid=$!
    if [ ! -z $PIXTER_CONTROL_NEEDED ]; then
        sleep 8
        send_command_to_pixter
    fi
    wait $pid
    retval=$?
    if [ ! -z $PIXTER_CONTROL_NEEDED ]; then
        reset_stop_pixter
    fi
else
    echo "Not supported yet"
    exit -1
fi

# check dump images.
if [ $I_TEST_TYPE == "error" ] || [ $I_TEST_TYPE == "negative" ]; then
    if [ $retval -eq 0 ];then
        RESULT="FAIL"
        DESCRIPTION="Error. error return code (${retval}) from APP, please refer to app log "
    fi
    #Check whether YUV file saved
    for((i=0; i<${CAMERA_NUM}; i++))
    do
        if [ ! -z ${DUMP_FILE_NAME[$i]} ] && [ -f ${DUMP_FILE_NAME[$i]} ];then
            image_size=`wc -c ${DUMP_FILE_NAME[$i]} | awk '{print $1}'`
            if [ $image_size -eq 0 ]; then
                RESULT="PASS"
                DESCRIPTION="The size of file ${DUMP_FILE_NAME[$i]} is 0 as expected."
            else
                RESULT="FAIL"
                DESCRIPTION="${DUMP_FILE_NAME[$i]} file size is not 0 but ${image_size}."
                break
            fi
        fi
    done    
else
    if [ $retval -ne 0 ]; then
        RESULT="FAIL"
        DESCRIPTION="Error return code from APP, please refer to app log"  
    else
        for((i=0; i<${CAMERA_NUM}; i++))
        do
            if [ ! -z ${DUMP_FILE_NAME[$i]} ]; then
                if [ ! -f ${DUMP_FILE_NAME[$i]} ]; then
                    RESULT="FAIL"
                    DESCRIPTION="${DUMP_FILE_NAME[$i]} file not exist."
                    break
                else
                    image_size=`wc -c ${DUMP_FILE_NAME[$i]} | awk '{print $1}'`
                    if [ $image_size -eq 0 ]; then
                        RESULT="FAIL"
                        DESCRIPTION="Error.The size of file ${DUMP_FILE_NAME[$i]} is 0."
                        break
                    fi
                fi
            fi
        done
    fi
fi

#check log file
echo "APP log ++++++++++++++++++++++++++++++++++++++++"
cat $LOG_FILE_NAME
echo "APP log ----------------------------------------"

if [ ! -f $LOG_FILE_NAME ]; then
    RESULT="TBD"
    DESCRIPTION="gst_messages.log file not exist."
elif [ ${printfps} == "true" ]; then
    fpsTarget=60
    if [ "${CAMERA_NUM}" == "4" ];then
        fpsTarget=30
    fi
    oldIFS="$IFS"
    IFS=$'\n'
    str_max_fps=(`grep "Average fps" $LOG_FILE_NAME | cut -d ',' -f 1`)
    str_min_fps=(`grep "Average fps" $LOG_FILE_NAME | cut -d ',' -f 2`)
    str_av_fps=(`grep "Average fps" $LOG_FILE_NAME | cut -d ',' -f 3`)
    IFS="$oldIFS"
    for((i=0; i<${CAMERA_NUM}; i++))
    do
        max_fps_single=${str_max_fps[$i]}
        min_fps_single=${str_min_fps[$i]}
        av_fps_single=${str_av_fps[$i]}
        
        max_fps=`echo ${max_fps_single:11}`
        min_fps=`echo ${min_fps_single:15}`
        av_fps=`echo ${av_fps_single:15}`
        
        compare_return=$(awk -v num1=$av_fps -v num2=$fpsTarget 'BEGIN{print(num1>num2)?"0":"1"}')
        #compare actual fps with target value
        if [ $compare_return -eq 1 ]; then
            RESULT="FAIL"
            DESCRIPTION="Error.Max fps is $max_fps, Min fps is $min_fps, Average fps is $av_fps, not hit the target."
            break
        elif [ $compare_return -eq 0 ]; then
            DESCRIPTION="Record $i:Max fps is $max_fps, Min fps is $min_fps, Average fps is $av_fps"
        fi
    done
#check whether xvimagesink can be launched normally
elif [ "$gstsink" == "xvimagesink" ] ; then 
    grep "error" $LOG_FILE_NAME | grep "fps-display-video_sink-actual-sink-vaapi"
    ret=$?
    if [ $ret -eq 0 ]; then
        RESULT="FAIL"
        DESCRIPTION="xvimagesink is failed to launch, please open GUI on device and try again."
    fi
fi
fi

for((i=0; i<${CAMERA_NUM}; i++))
do
    if [ ! -z "${DUMP_FILE_NAME[$i]}" ]; then
        rm ${DUMP_FILE_NAME[$i]}
    fi
done

chmod +x ${SW_VAL_ROOT}/scripts/tools/check_dmesg_error.sh
${SW_VAL_ROOT}/scripts/tools/check_dmesg_error.sh

echo "Test Case: $CASE_NAME"
echo "Result: $RESULT"
echo "Description: $DESCRIPTION"

if [ $RESULT == "PASS" ]; then
    exit 0
else
    exit -1
fi

