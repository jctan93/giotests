#!/bin/bash

if [ $# -lt 1 ] ; then
    echo "USAGE: $0 CASE_NAME"
    exit 1;
fi

CASE_NAME_LOWER=`echo $1 | tr '[A-Z]' '[a-z]'`

CAMERA_NUM=1
if [ ! -z `echo $CASE_NAME_LOWER | grep -i "DUAL_CAMERA"` ];then
    CAMERA_NUM=2
fi
if [ ! -z `echo $CASE_NAME_LOWER | grep -i "FOUR_CAMERA"` ];then
    CAMERA_NUM=4
fi
declare -a I_RESOLUTION
declare -a I_PIXEL_FORMAT
declare -a I_MEMORY_TYPE
declare -a I_IS_BLOCK_MODE
declare -a IS_INTERLACED
declare -a FILED_ORDER
declare -a WIDTH
declare -a HEIGHT

declare -a PIXEL_FORMAT
declare -a FORMAT
declare -a MEMORY_TYPE
declare -a IS_BLOCK_MODE
declare -a IS_INTERLACED


if [ "$CAMERA_NUM" == "1" ];then
    I_LAST=`echo $CASE_NAME_LOWER | awk -F_ '{print $(NF)}'`
    if [ $I_LAST == "xres" ]; then
        get_random_res
        I_MEMORY_TYPE=`echo $CASE_NAME_LOWER | awk -F_ '{print $(NF-1)}'`
        I_IS_BLOCK_MODE=`echo $CASE_NAME_LOWER | awk -F_ '{print $(NF-2)}'`
    elif [ $I_LAST == "interlaced" ]; then
        I_RESOLUTION=`echo $CASE_NAME_LOWER | awk -F_ '{print $(NF-1)}'`
        I_PIXEL_FORMAT=`echo $CASE_NAME_LOWER | awk -F_ '{print $(NF-2)}'`
        I_MEMORY_TYPE=`echo $CASE_NAME_LOWER | awk -F_ '{print $(NF-3)}'`
        I_IS_BLOCK_MODE=`echo $CASE_NAME_LOWER | awk -F_ '{print $(NF-4)}'`
        IS_INTERLACED='true'
        FILED_ORDER=V4L2_FIELD_ALTERNATE
        WIDTH=`echo $I_RESOLUTION | awk -Fx '{print $(1)}'`
        HEIGHT=`echo $I_RESOLUTION | awk -Fx '{print $(2)}'`
    else
        I_RESOLUTION=$I_LAST
        FILED_ORDER=V4L2_FIELD_NONE
        I_PIXEL_FORMAT=`echo $CASE_NAME_LOWER | awk -F_ '{print $(NF-1)}'`
        I_MEMORY_TYPE=`echo $CASE_NAME_LOWER | awk -F_ '{print $(NF-2)}'`
        I_IS_BLOCK_MODE=`echo $CASE_NAME_LOWER | awk -F_ '{print $(NF-3)}'`
        IS_INTERLACED='false'
        WIDTH=`echo $I_RESOLUTION | awk -Fx '{print $(1)}'`
        HEIGHT=`echo $I_RESOLUTION | awk -Fx '{print $(2)}'`
    fi

elif [ "$CAMERA_NUM" == "2" ] || [ "$CAMERA_NUM" == "4" ];then
    if [ "$CAMERA_NUM" == "2" ];then
        CAM1_CONFIG=${CASE_NAME_LOWER##*cam1_}
        CAM1_LEFT=${CASE_NAME_LOWER%%_cam1_*}
        CAM0_CONFIG=${CAM1_LEFT##*cam0_}
        CAM_CONFIGS=(${CAM0_CONFIG} ${CAM1_CONFIG})
    fi
    if [ "$CAMERA_NUM" == "4" ];then
        CAM3_CONFIG=${CASE_NAME_LOWER##*cam3_}
        CAM3_LEFT=${CASE_NAME_LOWER%%_cam3_*}
        CAM2_CONFIG=${CAM3_LEFT##*cam2_}
        CAM2_LEFT=${CAM3_LEFT%%_cam2_*}
        CAM1_CONFIG=${CAM2_LEFT##*cam1_}
        CAM1_LEFT=${CAM2_LEFT%%_cam1_*}
        CAM0_CONFIG=${CAM1_LEFT##*cam0_}
        CAM_CONFIGS=(${CAM0_CONFIG} ${CAM1_CONFIG} ${CAM2_CONFIG} ${CAM3_CONFIG})
    fi
    i=0
    for CAM_CONFIG in ${CAM_CONFIGS[*]}
    do
        I_RESOLUTION[$i]=`echo $CAM_CONFIG | awk -F_ '{print $(NF-1)}'`
        I_PIXEL_FORMAT[$i]=`echo $CAM_CONFIG | awk -F_ '{print $(NF)}'`
        I_MEMORY_TYPE[$i]="userptr"
        I_IS_BLOCK_MODE[$i]="noblock"
        IS_INTERLACED[$i]="false"
        FILED_ORDER[$i]=V4L2_FIELD_NONE
        WIDTH[$i]=`echo ${I_RESOLUTION[$i]} | awk -Fx '{print $(1)}'`
        HEIGHT[$i]=`echo ${I_RESOLUTION[$i]} | awk -Fx '{print $(2)}'`
        echo "I_RESOLUTION[$i]=${I_RESOLUTION[$i]}, I_PIXEL_FORMAT[$i]=${I_PIXEL_FORMAT[$i]}, I_MEMORY_TYPE[$i]=${I_MEMORY_TYPE[$i]}, I_IS_BLOCK_MODE[$i]=${I_IS_BLOCK_MODE[$i]}, I_IS_BLOCK_MODE[$i]=${I_IS_BLOCK_MODE[$i]}, FILED_ORDER[$i]=${FILED_ORDER[$i]}, WIDTH[$i]=${WIDTH[$i]}, HEIGHT[$i]=${HEIGHT[$i]}"
        i=$((i+1))
    done
else
    echo "Not configured to parse this case name"
    exit 1
fi
# if the last one is resolution/HEIGHT information, then
for ((i=0; i<${#HEIGHT[@]}; i++))
do
    if [ ! -z ${HEIGHT[$i]} ] ; then
        if [ ${IS_INTERLACED[$i]} == 'true' ]; then
            HEIGHT[$i]=`expr ${HEIGHT[$i]} / 2`
        fi

        if [ ! -z ${I_PIXEL_FORMAT[$i]} ] ; then
            if [ "${I_PIXEL_FORMAT[$i]}" == "raw8" ] ; then
                PIXEL_FORMAT[$i]=V4L2_PIX_FMT_SGRBG8
                FORMAT[$i]=SGRBG8
            elif [ "${I_PIXEL_FORMAT[$i]}" == "yuv422" ] || [ "${I_PIXEL_FORMAT[$i]}" == "uyvy" ] ; then
                PIXEL_FORMAT[$i]=V4L2_PIX_FMT_UYVY
                FORMAT[$i]=UYVY
            elif [ "${I_PIXEL_FORMAT[$i]}" == "raw10" ] ; then
                PIXEL_FORMAT[$i]=V4L2_PIX_FMT_SGRBG10
                FORMAT[$i]=SGRBG10
            elif [ "${I_PIXEL_FORMAT[$i]}" == "rgb24" ] || [ "${I_PIXEL_FORMAT[$i]}" == "rgb888" ] ; then
                PIXEL_FORMAT[$i]=V4L2_PIX_FMT_BGR24
                FORMAT[$i]=RGB24
            elif [ "${I_PIXEL_FORMAT[$i]}" == "rgb16" ] || [ "${I_PIXEL_FORMAT[$i]}" == "rgb565" ] ; then
                PIXEL_FORMAT[$i]=V4L2_PIX_FMT_RGB565
                FORMAT[$i]=RGB565
            elif [ "${I_PIXEL_FORMAT[$i]}" == "uyvy" ]; then
                PIXEL_FORMAT[$i]=V4L2_PIX_FMT_UYVY
                FORMAT[$i]=UYVY
            elif [ "${I_PIXEL_FORMAT[$i]}" == "yuyv" ]; then
                PIXEL_FORMAT[$i]=V4L2_PIX_FMT_YUYV
                FORMAT[$i]=YUYV
            fi
        fi

        if [ ! -z ${I_MEMORY_TYPE[$i]} ] ; then
            if [ ${I_MEMORY_TYPE[$i]} == "mmap" ] ; then
                MEMORY_TYPE[$i]=V4L2_MEMORY_MMAP
            elif [ ${I_MEMORY_TYPE[$i]} == "userptr" ] ; then
                MEMORY_TYPE[$i]=V4L2_MEMORY_USERPTR
            elif [ ${I_MEMORY_TYPE[$i]} == "dmabuf" ] ; then
                MEMORY_TYPE[$i]=V4L2_MEMORY_DMABUF
            else
                MEMORY_TYPE[$i]=V4L2_MEMORY_MMAP
            fi
        fi

        if [ ! -z ${I_IS_BLOCK_MODE[$i]} ] ; then
            if [ ${I_IS_BLOCK_MODE[$i]} == "block" ] ; then
                IS_BLOCK_MODE[$i]="true"
            elif [ ${I_IS_BLOCK_MODE[$i]} == "noblock" ] ; then
                IS_BLOCK_MODE[$i]="false"
            else
                IS_BLOCK_MODE[$i]="false"
            fi
        fi

        echo "config for cam${i} is resolution:${WIDTH[$i]}x${HEIGHT[$i]} format:${PIXEL_FORMAT[$i]} memory_type:${MEMORY_TYPE[$i]} block_mode:${IS_BLOCK_MODE[$i]} interlaced_mode:${IS_INTERLACED[$i]}"
        if [ -z ${IS_BLOCK_MODE[$i]} ] || [ -z ${MEMORY_TYPE[$i]} ] || [ -z ${PIXEL_FORMAT[$i]} ] || [ -z ${WIDTH[$i]} ]; then
            echo "Failed to parse case info"
            exit 1
        fi
    fi
done

