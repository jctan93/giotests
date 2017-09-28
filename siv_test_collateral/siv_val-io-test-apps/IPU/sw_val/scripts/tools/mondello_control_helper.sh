#!/bin/bash

function get_mondello_command_according_res_info()
{
    local resolution=$1
    local iformat=$2
    local is_interlaced=$3

    MONDELLO_COMMAND=''

    if [ $resolution == '1920x1080' ]; then
        if [ $iformat == 'yuv422' ]; then
            # 1920x1080 yuv422 interlaced
            if [ $is_interlaced == 'true' ]; then
                MONDELLO_COMMAND="yuv422_1080i_2lane.py"
            # 1920x1080 yuv422 progressive
            else
                MONDELLO_COMMAND="yuv422_1080p_4lane.py"
            fi
        elif [ $iformat == 'rgb24' ] || [ "$iformat" == "rgb888" ]; then
            # 1920x1080 rgb24 progressive
            if [ $is_interlaced == 'false' ]; then
                MONDELLO_COMMAND="rgb888_1080p_4lane.py"
            # 1920x1080 rgb24 interlaced
            else
                MONDELLO_COMMAND="rgb888_1080i_2lane.py"
            fi
        elif [ "$iformat" == "rgb565" ] || [ "$iformat" == "rgb16" ]; then
            # 1920x1080 rgb565 progressive
            if [ $is_interlaced == 'false' ]; then
                MONDELLO_COMMAND="rgb565_1080p_4lane.py"
            # 1920x1080 rgb565 interlaced
            else
                MONDELLO_COMMAND="rgb565_1080i_2lane.py"
            fi
        fi
    elif [ $resolution == '720x576' ]; then
        if [ $iformat == 'yuv422' ]; then
            # 720x576 yuv422 interlaced
            if [ $is_interlaced == 'true' ]; then
                MONDELLO_COMMAND="yuv422_576i_1lane.py"
            # 720x576 yuv422 progressive
            else
                MONDELLO_COMMAND="yuv422_576p_1lane.py"
            fi
        elif [ $iformat == 'rgb24' ] || [ "$iformat" == "rgb888" ]; then
            # 720x576 rgb24 progressive
            if [ $is_interlaced == 'false' ]; then
                MONDELLO_COMMAND="rgb888_576p_1lane.py"
            # 720x576 rgb24 interlaced
            else
                MONDELLO_COMMAND="rgb888_576i_1lane.py"
            fi
        elif [ "$iformat" == "rgb565" ] || [ "$iformat" == "rgb16" ]; then
            # 720x576 rgb565 progressive
            if [ $is_interlaced == 'false' ]; then
                MONDELLO_COMMAND="rgb565_576p_1lane.py"
            # 720x576 rgb565 interlaced
            else
                MONDELLO_COMMAND="rgb565_576i_1lane.py"
            fi
        fi
    elif [ $resolution == '640x480' ]; then
        if [ $iformat == 'yuv422' ]; then
            # 640x480 yuv422 progressive
            if [ $is_interlaced == 'false' ]; then
                MONDELLO_COMMAND="yuv422_vga_1lane.py"
            fi
        elif [ $iformat == 'rgb24' ] || [ "$iformat" == "rgb888" ]; then
            # 640x480 rgb24 progressive
            if [ $is_interlaced == 'false' ]; then
                MONDELLO_COMMAND="rgb888_vga_1lane.py"
            fi
        elif [ "$iformat" == "rgb565" ] || [ "$iformat" == "rgb16" ]; then
            # 640x480 rgb565 progressive
            if [ $is_interlaced == 'false' ]; then
                MONDELLO_COMMAND="rgb565_vga_1lane.py"
            fi
        fi
    elif [ $resolution == '1280x720' ]; then
        if [ $iformat == 'yuv422' ]; then
            # 1280x720 yuv422 progressive
            if [ $is_interlaced == 'false' ]; then
                MONDELLO_COMMAND="yuv422_720p_4lane.py"
            fi
        elif [ "$iformat" == "rgb24" ] || [ "$iformat" == "rgb888" ]; then
            # 1280x720 rgb24 progressive
            if [ $is_interlaced == 'false' ]; then
                MONDELLO_COMMAND="rgb888_720p_4lane.py"
            fi
        elif [ "$iformat" == "rgb16" ] || [ "$iformat" == "rgb565" ]; then
            # 1280x720 rgb565 progressive
            if [ $is_interlaced == 'false' ]; then
                MONDELLO_COMMAND="rgb565_720p_4lane.py"
            fi
        fi
    elif [ $resolution == '720x480' ]; then
        if [ $iformat == 'yuv422' ]; then
            # 720x480 yuv422 interlaced
            if [ $is_interlaced == 'true' ]; then
                MONDELLO_COMMAND="yuv422_480i_1lane.py"
            fi
        elif [ $iformat == 'rgb24' ] || [ "$iformat" == "rgb888" ]; then
            # 720x480 rgb24 interlaced
            if [ $is_interlaced == 'true' ]; then
                MONDELLO_COMMAND="rgb888_480i_1lane.py"
            fi
        elif [ "$iformat" == "rgb565" ] || [ "$iformat" == "rgb16" ]; then
            # 720x480 rgb565 interlaced
            if [ $is_interlaced == 'true' ]; then
                MONDELLO_COMMAND="rgb565_480i_1lane.py"
            fi
        fi
    fi
}

function send_command_to_mondello_server()
{
    #to compatible with existing single cam cases and reuse for new multi cam cases, 
    #for existing single cam case, argument num is 0, so no need no change.
    #for new multi cam cases, need to pass server ip and cmd to this function.
    if [ $# -eq 2 ];then
        local MONDELLO_SERVER_IP=$1
        local MONDELLO_COMMAND=$2
    fi

    if [ -z ${MONDELLO_SERVER_IP} ];then
        echo "MONDELLO_SERVER_IP is empty"
    fi

    if [ ! -z "$MONDELLO_COMMAND" ] ; then
        echo "Mondello command: ${MONDELLO_COMMAND}"
        echo $MONDELLO_COMMAND > /dev/udp/$MONDELLO_SERVER_IP/13579
        echo "UDP send Mondello Command, Done!"
    else
        echo "Mondello Command is empty"
    fi
}

function reconnect_to_mondello_server()
{
    #to compatible with existing single cam cases and reuse for new multi cam cases, 
    #for existing single cam case, argument num is 0, so no need no change.
    #for new multi cam cases, need to pass server ip and cmd to this function.
    if [ $# -eq 2 ];then
        local MONDELLO_SERVER_IP=$1
        local MONDELLO_COMMAND=$2
    fi

    if [ -z ${MONDELLO_SERVER_IP} ];then
        echo "MONDELLO_SERVER_IP is empty"
    fi

    if [ ! -z "$MONDELLO_COMMAND" ] ; then
        echo "Reconnect mondello with server ip $MONDELLO_SERVER_IP"
        exec 6<>/dev/tcp/$MONDELLO_SERVER_IP/65432
        echo -e "reconnect">&6
        exec 6<&-
        exec 6>&-
        echo "Reconnect mondello $MONDELLO_SERVER_IP done"
    else
        echo "Mondello Command is empty"
    fi
}