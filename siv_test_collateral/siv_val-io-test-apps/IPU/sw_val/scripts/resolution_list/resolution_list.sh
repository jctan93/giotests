#!/bin/bash

if [ $# -lt 1 ] ; then 
    echo "USAGE: $0 media_config" 
    exit 1; 
fi

media_config=$1

if [ ! -z $(echo $media_config | grep "adv7481") ] ; then
    . /home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/scripts/resolution_list/adv7481.sh
elif [  ! -z $(echo $media_config | grep "tpg") ] ; then
    . /home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/scripts/resolution_list/tpg.sh
elif [  ! -z $(echo $media_config | grep "imx185") ] ; then
    . /home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/scripts/resolution_list/imx185.sh
fi

function get_res_by_index()
{
    local index=$1
    local count=${#RESOLUTION_LIST[*]}
    
    if [ $count > 0 ] && [ ! -z "${index}" ]; then
        I_RESOLUTION=${RESOLUTION_LIST[$index]}
        WIDTH=`echo $I_RESOLUTION | awk -Fx '{print $(1)}'`
        HEIGHT=`echo $I_RESOLUTION | awk -Fx '{print $(2)}'`
        I_PIXEL_FORMAT=${FORMAT_LIST[$index]}
        IS_INTERLACED=${INTERLACED_MODE[$index]}
        if [ "$IS_INTERLACED" == "true" ]; then
            FILED_ORDER=V4L2_FIELD_ALTERNATE
        else
            FILED_ORDER=V4L2_FIELD_NONE
        fi
    fi   
}

function get_random_res()
{
    local count=${#RESOLUTION_LIST[*]}
    local randi=$( expr $RANDOM % $count )
    
    get_res_by_index $randi
}

function get_default_res()
{
    get_res_by_index $DEFAULT_RESULITON_INDEX
}