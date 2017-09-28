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

# I_TEST_TYPE is not an array. Cams used the same.
declare -a I_PIXEL_FORMAT
declare -a I_RESOLUTION
declare -a I_INTERLACED
declare -a I_DEINTERLACE

declare -a FORMAT
declare -a MONDELLO_FORMAT
declare -a interlace_mode
declare -a WIDTH
declare -a HEIGHT
declare -a DUMP_FILE_NAME
declare -a gstsink
wdr_mode=auto 

# num_buffers is not an array. Cams used the same.
# deinterlace_method is not an array. Only single cam need this.
# printfps is not an array. Cams used the same.

if [ "$CAMERA_NUM" == "1" ];then
    I_TEST_TYPE=`echo $CASE_NAME_LOWER | awk -F_ '{print $(5)}'`
    I_PIXEL_FORMAT=`echo $CASE_NAME_LOWER | awk -F_ '{print $(6)}'`
    I_RESOLUTION=`echo $CASE_NAME_LOWER | awk -F_ '{print $(7)}'`
    I_INTERLACED=`echo $CASE_NAME_LOWER | awk -F_ '{print $(8)}'`
    I_DEINTERLACE=`echo $CASE_NAME_LOWER | awk -F_ '{print $(9)}'`
    WIDTH=`echo $I_RESOLUTION | awk -Fx '{print $(1)}'`
    HEIGHT=`echo $I_RESOLUTION | awk -Fx '{print $(2)}'`
    
    if [ $I_TEST_TYPE == "60fps" ]; then
        printfps=true
        num_buffers=500
        gstsink=fakesink
    elif [ $I_TEST_TYPE == "check" ]; then
        if [ $cameraInput == "imx185" ]; then
            printfps=false
            num_buffers=50
            io_mode=3
            wdr_mode=auto
            gstsink="yamiscale ! video/x-raw,format=xBGR,width=1920,height=1080 ! yamisink"
        else
            printfps=false
            num_buffers=100
            gstsink="videoconvert ! autovideosink"
        fi
    elif [ $I_TEST_TYPE == "display" ]; then
        printfps=false
        num_buffers=100
        DUMP_FILE_NAME="${CASE_NAME}.mp4"
        if [ "$PROJECT_CODE" == "BMW"  ] && [ "$FORMAT" == "UYVY" ] && [ "$interlace_mode" == "false" ]; then
            gstsink="tee name=t ! queue ! mfxvpp ! mfxsink t. ! queue ! filesink location=${DUMP_FILE_NAME}"
        else
            gstsink="tee name=t ! queue ! videoconvert ! autovideosink t. ! queue ! vaapih264enc ! mp4mux ! filesink location=${DUMP_FILE_NAME}"
        fi
    elif [ $I_TEST_TYPE == "duration" ]; then
        printfps=false
        num_buffers=100
        DUMP_FILE_NAME="${CASE_NAME}.raw"
        gstsink="filesink location=${DUMP_FILE_NAME}"
    elif [ $I_TEST_TYPE == "error" ]; then
        printfps=false
        num_buffers=1
        DUMP_FILE_NAME="${CASE_NAME}.raw"
        gstsink="filesink location=${DUMP_FILE_NAME}"
    elif [ $I_TEST_TYPE == "single" ]; then
        printfps=false
        num_buffers=1
        DUMP_FILE_NAME="${CASE_NAME}.raw"
        gstsink="filesink location=${DUMP_FILE_NAME}"
    elif [ $I_TEST_TYPE == "si" ]; then
        printfps=false
        num_buffers=1
        DUMP_FILE_NAME="${CASE_NAME}.jpg"
        gstsink="videoconvert ! jpegenc ! filesink location=${DUMP_FILE_NAME}"
    elif [ $I_TEST_TYPE == "vr" ]; then
        printfps=false
        num_buffers=1000
        DUMP_FILE_NAME="${CASE_NAME}.avi"
        gstsink="avimux ! filesink location=${DUMP_FILE_NAME}"
    elif [ $I_TEST_TYPE == "dmabufimport" ]; then
        printfps=false
        num_buffers=100
        io_mode=3
        DUMP_FILE_NAME="${CASE_NAME}.raw"
        if [ "$PROJECT_CODE" == "BMW"  ] && [ "$FORMAT" == "UYVY" ] && [ "$interlace_mode" == "false" ]; then
            gstsink="mfxvpp ! tee name=t ! queue !  mfxsink t. ! queue ! filesink location=${DUMP_FILE_NAME}"
        else
            gstsink="vaapipostproc ! tee name=t ! queue !  vaapisink t. ! queue ! filesink location=${DUMP_FILE_NAME}"
        fi
    elif [ $I_TEST_TYPE == "dmabufimport60fps" ]; then
        printfps=true
        num_buffers=500
        io_mode=3
        gstsink="vaapipostproc ! vaapisink"
    elif [ $I_TEST_TYPE == "vhdr" ]; then
        printfps=false
        num_buffers=500
        io_mode=3
        wdr_mode=on
        gstsink="yamiscale ! video/x-raw,format=xBGR,width=1920,height=1080 ! yamisink"
    elif [ $I_TEST_TYPE == "vull" ]; then
        printfps=false
        num_buffers=500
        io_mode=3
        wdr_mode=off
        gstsink="yamiscale ! video/x-raw,format=xBGR,width=1920,height=1080 ! yamisink"
    fi
    #UYVY fomat and interlaced mode of RGB can only use vaapipostproc and vaapisink instead of videoconvert and autovideosink. This makes it complex.
    if [ "$I_PIXEL_FORMAT" == "uyvy" ] || [ "$I_PIXEL_FORMAT" == "yuy2" ] || [ "$I_INTERLACED" == "interlaced" ];then
        gstsink=${gstsink//videoconvert/vaapipostproc}
        gstsink=${gstsink//autovideosink/vaapisink}
    fi
    if [ ! -z $I_DEINTERLACE ] && [ $I_DEINTERLACE == 'deinterlace' ]; then
        deinterlace_method=sw_bob
    fi
elif [ "$CAMERA_NUM" == "2" ] || [ "$CAMERA_NUM" == "4" ];then
    I_TEST_TYPE=`echo $CASE_NAME_LOWER | awk -F_ '{print $(3)}'`
    if [ "$CAMERA_NUM" == "2" ];then
        CAM1_CONFIG=${CASE_NAME_LOWER##*cam1_}
        CAM1_LEFT=${CASE_NAME_LOWER%%_cam1_*}
        CAM0_CONFIG=${CAM1_LEFT##*cam0_}
        CAM_CONFIGS=(${CAM0_CONFIG} ${CAM1_CONFIG})
    else
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
        I_INTERLACED[$i]="progressive"
        WIDTH[$i]=`echo ${I_RESOLUTION[$i]} | awk -Fx '{print $(1)}'`
        HEIGHT[$i]=`echo ${I_RESOLUTION[$i]} | awk -Fx '{print $(2)}'`
        DUMP_FILE_NAME[$i]="${CASE_NAME}_CAM$i.raw"
        gstsink[$i]="filesink location=${DUMP_FILE_NAME[$i]}"
        echo "I_RESOLUTION[$i]=${I_RESOLUTION[$i]}, I_PIXEL_FORMAT[$i]=${I_PIXEL_FORMAT[$i]},WIDTH[$i]=${WIDTH[$i]}, HEIGHT[$i]=${HEIGHT[$i]}, I_INTERLACED[$i]=${I_INTERLACED[$i]}, DUMP_FILE_NAME[$i]=${DUMP_FILE_NAME[$i]}, gstsink[$i]=${gstsink[$i]}"
        i=$((i+1))
    done
    
    # default values for function test
    printfps=false
    num_buffers=100
    if [ "$CAMERA_NUM" == "4" ];then
        num_buffers=20
    fi    
    if [ "${I_TEST_TYPE}" == "perf" ]; then
        printfps=true
        num_buffers=500
        for((i=0; i<$CAMERA_NUM; i++))
        do
            gstsink[$i]="fakesink"
            DUMP_FILE_NAME[$i]=
        done
    fi
else
    echo "Not configured to parse this case name"
    exit 1
fi

for ((i=0; i<${#I_PIXEL_FORMAT[@]}; i++))
do
    if [ ${I_PIXEL_FORMAT[$i]} == 'yuy2' ]; then
        if [ "$cameraInput" == "mondello" ]; then
            FORMAT[$i]=UYVY
            MONDELLO_FORMAT[$i]=yuv422
        elif [ "$cameraInput" == "aggregator" ]; then
            FORMAT[$i]=UYVY
        else
            FORMAT[$i]=YUY2
        fi
    elif [ ${I_PIXEL_FORMAT[$i]} == 'rgb24' ]  || [ ${I_PIXEL_FORMAT[$i]} == 'rgb888' ]; then
        #progressive use old format， interlaced use new format!!
        if [ ${I_INTERLACED[$i]} == 'interlaced' ]; then
            FORMAT[$i]=BGRx
        else
            FORMAT[$i]=BGR
        fi
        if [ "$cameraInput" == "mondello" ]; then
            MONDELLO_FORMAT[$i]=rgb24
        fi
    elif [ ${I_PIXEL_FORMAT[$i]} == 'rgb565' ] || [ ${I_PIXEL_FORMAT[$i]} == 'rgb16' ]; then
        #progressive use old format， interlaced use new format!!
        if [ ${I_INTERLACED[$i]} == 'interlaced' ]; then
            FORMAT[$i]=RGBx
        else
            FORMAT[$i]=RGB16
        fi
        if [ "$cameraInput" == "mondello" ]; then
            MONDELLO_FORMAT[$i]=rgb565
        fi
    elif [ ${I_PIXEL_FORMAT[$i]} == 'i420' ]; then
        FORMAT[$i]=I420
        MONDELLO_FORMAT[$i]=''
    elif [ ${I_PIXEL_FORMAT[$i]} == 'nv12' ]; then
        FORMAT[$i]=NV12
        MONDELLO_FORMAT[$i]=''
    # UYVY and YUVY are for ov10635 real sensors. Mondello is not needed.
    elif [ ${I_PIXEL_FORMAT[$i]} == 'uyvy' ];then
        FORMAT[$i]=UYVY
    elif [ ${I_PIXEL_FORMAT[$i]} == 'yuyv' ];then
        FORMAT[$i]=YUYV
    fi

    if [ ${I_INTERLACED[$i]} == 'interlaced' ]; then
        interlace_mode[$i]=true
        
    elif [ ${I_INTERLACED[$i]} == 'progressive' ]; then
        interlace_mode[$i]=false
    fi
done

for ((i=0; i<${CAMERA_NUM}; i++))
do
    echo "width$i: ${WIDTH[$i]}, height$i: ${HEIGHT[$i]}, format$i: ${FORMAT[$i]}, num_buffers: ${num_buffers}, \
    interlaced$i: ${interlace_mode[$i]}, deinterlace_method: ${deinterlace_method} printfps: ${printfps}"

    if [ -z ${WIDTH[$i]} ] || [ -z ${HEIGHT[$i]} ] || [ -z $num_buffers ] || [ -z ${FORMAT[$i]} ]; then
        echo "Failed to parse info from case name"
    fi
done    
