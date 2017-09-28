#!/bin/bash

RESULT="PASS"
DESCRIPTION=""
SW_VAL_ROOT=/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val

if [ $# -lt 2 ] ; then
    echo "USAGE: $0 CASE_NAME GTEST_CASE_FILTER [MEDIA_CONFIG_COMMAND]"
    exit 1;
fi

CASE_NAME=$1 # like: CI_TPG_IPU4_IOCTL_Capture_Frame_1_Block_Mmap_Raw8_640x480
GTEST_CASE_FILTER=$2

if [ $# -gt 2 ] ; then
    MEDIA_CONFIG_COMMAND=$3
    . ${SW_VAL_ROOT}/scripts/resolution_list/resolution_list.sh $MEDIA_CONFIG_COMMAND
fi

echo 'Parse info from case name'
. ${SW_VAL_ROOT}/scripts/tools/parse_v4l2_case_name.sh $CASE_NAME

echo 'Run media config and init resolution list'
if [ ! -z $MEDIA_CONFIG_COMMAND ] ; then
    echo 'Change to execution dir ${SW_VAL_ROOT}/results'
    LOG_DIR=${SW_VAL_ROOT}/results
    if [ ! -d $LOG_DIR ]; then
        mkdir $LOG_DIR
    fi
    cd $LOG_DIR
    if [ "${CAMERA_NUM}" == "1" ] || [ -z ${CAMERA_NUM} ];then
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        echo "Media config: . ${SW_VAL_ROOT}/scripts/media_config/${MEDIA_CONFIG_COMMAND} ${FORMAT} ${WIDTH}x${HEIGHT}"
        . ${SW_VAL_ROOT}/scripts/media_config/${MEDIA_CONFIG_COMMAND} $FORMAT "${WIDTH}x${HEIGHT}" $IS_INTERLACED
        echo "-----------------------------------------------------------------------------"
        if [ -z $DEV_NAME ]; then
            echo "DEV_NAME is not initialized"
            exit -1
        fi

        if [ ! -z $MONDELLO_CONTROL_NEEDED ]; then
            echo "Get mondello script name according to resolution information $I_RESOLUTION $I_PIXEL_FORMAT $IS_INTERLACED"
            get_mondello_command_according_res_info $I_RESOLUTION $I_PIXEL_FORMAT $IS_INTERLACED
        fi
        
        if [ ! -z $MONDELLO_CONTROL_NEEDED ]; then
            reconnect_to_mondello_server
            sleep 5
        fi
        APP_LOG_FILE_NAME="${CASE_NAME}.log"
        DUMP_PREFIX="${CASE_NAME}"
        chmod +x ${SW_VAL_ROOT}/bin/ipu4_v4l2_test

        echo 'Run test app'
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        echo "App command: ${SW_VAL_ROOT}/bin/ipu4_v4l2_test --gtest_filter=$GTEST_CASE_FILTER -d=$DEV_NAME -i=$IS_BLOCK_MODE -f=$FILED_ORDER \
        -m=$MEMORY_TYPE -p=$PIXEL_FORMAT -w=$WIDTH -h=$HEIGHT -c="pwd" -r=$CASE_NAME"
        ${SW_VAL_ROOT}/bin/ipu4_v4l2_test --gtest_filter=$GTEST_CASE_FILTER -d=$DEV_NAME -i=$IS_BLOCK_MODE -f=$FILED_ORDER \
        -m=$MEMORY_TYPE -p=$PIXEL_FORMAT -w=$WIDTH -h=$HEIGHT -c="pwd" -r=$CASE_NAME >  $APP_LOG_FILE_NAME &
        pid=$!
        echo "-----------------------------------------------------------------------------"

        if [ ! -z $MONDELLO_CONTROL_NEEDED ]; then
            sleep 5
            send_command_to_mondello_server
        fi

        wait $pid

        if [ $? -ne 0  ]; then
            RESULT="FAIL"
            DESCRIPTION="Error, please refer to ${APP_LOG_FILE_NAME}."
        fi
    elif [ "${CAMERA_NUM}" == "2" ] || [ "${CAMERA_NUM}" == "4" ];then
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        echo "Media config for ${CAMERA_NUM} cams: . ${SW_VAL_ROOT}/scripts/media_config/${MEDIA_CONFIG_COMMAND} FORMAT[@] WIDTH[@] HEIGHT[@] IS_INTERLACED[@]"
        . ${SW_VAL_ROOT}/scripts/media_config/${MEDIA_CONFIG_COMMAND} FORMAT[@] WIDTH[@] HEIGHT[@] IS_INTERLACED[@]
        i=1
        for dev_name in ${DEV_NAME[*]}
        do
            if [ -z ${dev_name} ];then
                echo "Camera $i is not initialized!"
                exit -1
            fi
            echo "Camera $i is initialized! DEV_NAME_$i=${dev_name}"
            i=$((i+1))
        done
        if [ ! -z $MONDELLO_CONTROL_NEEDED ]; then
            echo "Get mondello script name according to resolution array \"${I_RESOLUTION[*]}\" \"${I_PIXEL_FORMAT[*]}\" \"${IS_INTERLACED[*]}\""
            get_mondello_command_arrays_according_res_array
        fi
        if [ ! -z $PIXTER_CONTROL_NEEDED ]; then
            echo "Get pixter command according to case name ${CASE_NAME}"
            get_pixter_command_by_casename
        fi
        if [ ! -z $MONDELLO_CONTROL_NEEDED ]; then
            reconnect_to_mondello_servers
            sleep 5
        fi
        
        APP_LOG_FILE_BASE_NAME="${CASE_NAME}"
        declare -a APP_LOG_FILE_NAME
        chmod +x ${SW_VAL_ROOT}/bin/ipu4_v4l2_test
        
        echo 'Run test apps'
        echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        i=0
        declare -a pids
        for dev_name in ${DEV_NAME[*]}
        do
            is_block_mode=${IS_BLOCK_MODE[$i]}
            field_order=${FILED_ORDER[$i]}
            memory_type=${MEMORY_TYPE[$i]}
            pixel_format=${PIXEL_FORMAT[$i]}
            width=${WIDTH[$i]}
            height=${HEIGHT[$i]}
            APP_LOG_FILE_NAME[$i]="${APP_LOG_FILE_BASE_NAME}_CAM$i.log"
            DUMP_PREFIX[$i]="${CASE_NAME}_CAM${i}_"
            if [ "${CAMERA_NUM}" == "2" ];then
                nstreams=2
            else
                nstreams=4
            fi
            echo "App command: ${SW_VAL_ROOT}/bin/ipu4_v4l2_test --gtest_filter=$GTEST_CASE_FILTER -d=$dev_name -i=$is_block_mode -f=$field_order \
            -m=$memory_type -p=$pixel_format -w=$width -h=$height -c="pwd" -r=${DUMP_PREFIX[$i]} "
            ${SW_VAL_ROOT}/bin/ipu4_v4l2_test --gtest_filter=$GTEST_CASE_FILTER -d=$dev_name -i=$is_block_mode -f=$field_order \
            -m=$memory_type -p=$pixel_format -w=$width -h=$height -c="pwd" -r=${DUMP_PREFIX[$i]}  > ${APP_LOG_FILE_NAME[$i]} &
            pids[$i]=$!
            i=$((i+1))
        done
        echo "-----------------------------------------------------------------------------"

        if [ ! -z $MONDELLO_CONTROL_NEEDED ]; then
            sleep 5
            send_command_arrary_to_mondello_servers
        fi
        if [ ! -z $PIXTER_CONTROL_NEEDED ]; then
            send_command_to_pixter
        fi
        echo "wait for pids ${pids[*]} to finish..."
        wait ${pids[*]}
        if [ $? -ne 0  ]; then
            RESULT="FAIL"
            DESCRIPTION="Error, please refer to ${APP_LOG_FILE_BASE_NAME}_CAM*.log."
        fi
        if [ ! -z $PIXTER_CONTROL_NEEDED ]; then
            reset_stop_pixter
        fi
    else
        echo "Not supported yet"
        exit -1
    fi
fi

for LOG in ${APP_LOG_FILE_NAME[*]}
do
    if [ ! -f ${LOG} ];then
    RESULT="TBD"
    DESCRIPTION="Log file ${LOG} not found."
        #break
    else
    echo "${LOG}:"
    cat ${LOG}
    grep "\[  FAILED  \] 1 test" ${LOG}
    if [ $? -eq 0 ]; then
        RESULT="FAIL"
        DESCRIPTION="Error, please refer to ${APP_LOG_FILE_NAME[*]}"
        #break
    fi
    fi
done

if [ "${RESULT}" == "PASS" ] && [ ! -z `echo $GTEST_CASE_FILTER | grep -i "_Frame"` ] && [ -z `echo $CASE_NAME | grep -i "PERF"` ] && [ -z `echo $CASE_NAME | grep -i "fps"` ]; then
    frame_num=`echo ${GTEST_CASE_FILTER#*_Frame_} | awk -F_ '{if ($1 ~ /^[0-9]+$/) print $1}'`
    if [ ! -z $frame_num ]; then
        for s_dump_prefix in ${DUMP_PREFIX[*]}
        do
            echo "Checking frames num got for ${s_dump_prefix}"
            image_num=`ls | grep -e  "${s_dump_prefix}[0-9]*.bin" | wc -l`
            if [ $frame_num -ne $image_num ]; then
                RESULT="FAIL"
                DESCRIPTION="Dump frame number wrong. Should be $frame_num, but exist $image_num for ${s_dump_prefix}."
                break
            fi
        done
   fi
fi

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
