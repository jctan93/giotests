#!/bin/bash
# Author: Henri Ngui (WWID 11472439)
# Created: June 2013

# UPDATE: 2013-07-17
# Change "-Dplughw" to "-D hw"

# UPDATE: 2013-07-21
# Added 3IA | 2IAFW option, added performance test measurement & result filtering, added stress test feature

# UPDATE: 2013-07-30
# Fixed bug for performance data csv file creator.

# UPDATE: 2013-09-01
# Added channel swap testing that will automatically append lines to /etc/profile & remove them when done
# A temporary log file will be created in the /root directory during the test to track the test

# UPDATE: 2013-09-17
# Changed 3IA I2S mode playback & recording to 24bit

# UPDATE: 2013-10-01
# Update Performance Data collection to include irq/26, irq/27, irq/28, irq/29

# UPDATE: 2013-10-25
# Added function to select audio file. WIP individual song for each SSP

# UPDATE: 2013-12-15
# Removed IAFW | IA Option form hardcode
# Fix to audio file selection for SSP0, SSP1 & FW SSP2
# Replaced hardcoded 48khz as freq variable

# USAGE: ./LPE_script3.sh [driver] [SSP0 mode] [SSP1 mode] [SSP2 mode] [Option] [test mode] [SSP port] [SSP port] [SSP port] [file] [SSP2 FW file]
# Driver         =  IAFW, IA
# SSP mode       =  tdm, i2s
# Option         =  aplay, arecord, arecord_aplay, pipe
# Test mode      =  performance, swap, test, stress
# SSP Port       =  SSP0, SSP1, SSP2 (optional)
# Duration       =  Placed at the end of the execution line (ONLY used with arecord, arecord_aplay option)
# SSP2 FW file   =  Used only when in IAFW mode for simultaneous playback of 32bit & 24bit audio file (ONLY used with IAFW mode aplay, arecord_aplay)

# Tip: To check the PLAY/RECORD count for CHANNEL SWAP TEST, execute "cat /root/SWAP_LOG_TEMP | grep swap_play_count" 

# =====================================================================
# HARDCODED DEFAULTS

# HARDCODED INTERNAL SWITCH for 3IA or 2IA & 1FW
test_mode="IAFW" # Options are [ IA | IAFW ]

dur=25 # Default duration of recording 20sec. Will be changed when running stress.

max_swap_play_count=100 # Number of iteration for swap mode test

buffer=2

freq=48000

# =====================================================================
# SET PARAMETERS
# TEST MODE 3IA or IAFW
if [ "$1" == "IA" ] || [ "$1" == "IAFW" ]; then
    test_mode="$1"
fi

# DURATION FOR RECORDING or PLAYBACK
if [ "$5" == "arecord" ] || [ "$5" == "arecord_aplay" ]; then
    if [ "$7" != "" ]; then
        if [ "$7" != "SSP0" ] && [ "$7" != "SSP1" ] && [ "$7" != "SSP2" ]; then
            dur=$7
        fi
    fi
    
    if [ "$8" != "" ]; then
        if [ "$8" != "SSP0" ] && [ "$8" != "SSP1" ] && [ "$8" != "SSP2" ]; then
            dur=$8
        fi
    fi
    
    if [ "$9" != "" ]; then
        if [ "$9" != "SSP0" ] && [ "$9" != "SSP1" ] && [ "$9" != "SSP2" ]; then
            dur=$9
        fi
    fi
fi
    
# SET PARAMETER FOR SSP0
hw0="hw:BYTSSP0"
if [ "$2" == "tdm" ]; then
    if [ "$test_mode" == "IA" ]; then
        plugin_0="IA_SSP_0_Xto8"
    else
        plugin_0="SSP_0_Xto8"
    fi
    rc0=8 # Recording channel count
    bit0="S32_LE"
elif [ "$2" == "i2s" ]; then
    if [ "$test_mode" == "IA" ]; then
        plugin_0="IA_SSP0_2ch"
    else
        plugin_0="SSP_0_2ch"
    fi
    rc0=2 # Recording channel count
    bit0="S24_LE"
else
    echo -e "Please enter correct mode for SSP0"
fi


# SET PARAMETER FOR SSP1
hw1="hw:BYTSSP1"
if [ "$3" == "tdm" ]; then
    if [ "$test_mode" == "IA" ]; then
        plugin_1="IA_SSP_1_Xto8"
    else
        plugin_1="SSP_1_Xto8"
    fi
    rc1=8 # Recording channel count
    bit1="S32_LE"
elif [ "$3" == "i2s" ]; then
    if [ "$test_mode" == "IA" ]; then
        plugin_1="IA_SSP1_2ch"

    else
        plugin_1="SSP_1_2ch"
    fi
    rc1=2 # Recording channel count
    bit1="S24_LE"
else
    echo -e "Please enter correct mode for SSP1"
fi


# SET PARAMETER FOR SSP2
if [ "$4" == "tdm" ]; then
    plugin_2="IA_SSP_2_Xto8" # for IA mode only. IAFW mode uses hw ID.
    rc2=8 # Recording channel count
    bit2="S32_LE"
elif [ "$4" == "i2s" ]; then
    plugin_2="IA_SSP2_2ch" # for IA mode only. IAFW mode uses hw ID.
    rc2=2 # Recording channel count
    bit2="S24_LE"
else
    echo -e "Please enter correct mode for SSP2"
fi

if [ "$test_mode" == "IA" ]; then 
    hw2="hw:BYTSSP2" 
else
    hw2="hw:0,0"
    bit2="S24_LE"
fi


# AUDIO FILE
if [ "$test_mode" == "IA" ]; then
    directory="/home/Music"
    if [ "$2" == "tdm" ]; then
        file0="/TDM8/32bit_48khz/8ch_32.wav"
    else
        file0="/48Khz_24_Glee1.wav"
    fi
    if [ "$3" == "tdm" ]; then
        file1="/TDM8/32bit_48khz/8ch_32.wav"
    else
        file1="/48Khz_24_Glee2.wav"
    fi
    if [ "$4" == "tdm" ]; then
        file2="/TDM8/32bit_48khz/8ch_32.wav"
    else
        file2="/48Khz_24_Glee3.wav"
    fi
    music0=$directory''$file0
    music1=$directory''$file1
    music2=$directory''$file2
elif [ "$test_mode" == "IAFW" ]; then
    directory="/home/Music"
    if [ "$2" == "tdm" ]; then 
        file0="/TDM8/32bit_48khz/8ch_32.wav"
    else
        file0="/48KHz_24_stereo.wav"
    fi
    if [ "$3" == "tdm" ]; then
        file1="/TDM8/32bit_48khz/8ch_32.wav"
    else
        file1="/48Khz_24_stereo.wav"
    fi
    if [ "$4" == "tdm" ]; then
        file2="/TDM8/24bit_48khz/8ch.wav"
    else
        file2="/48Khz_24_stereo.wav"
    fi
    music0=$directory''$file0
    music1=$directory''$file1
    music2=$directory''$file2
else
    echo -e "Please enter either IA or IAFW"
fi


# FILE OPTIONS PARAMETER

#if [ "$8" != "" ] && [ [ "$8" != "SSP0" ] || [ "$8" != "SSP1" ] || [ "$8" != "SSP2" ] ]; then
if [ "$7" != "" ] && [ "$7" != "SSP0" ]; then
    music0="$7"
    music1="$7"
    music2="$7"
fi

#if [ "$9" != "" ] && [ [ "$9" != "SSP0" ] || [ "$9" != "SSP1" ] || [ "$9" != "SSP2" ] ]; then
if [ "$8" != "" ] && [ "$8" != "SSP1" ]; then
    music0="$8"
    music1="$8"
    music2="$8"
fi

#if [ "$9" != "" ] && [ [ "$9" != "SSP0" ] || [ "$9" != "SSP1" ] || [ "$9" != "SSP2" ] ]; then
if [ "$9" != "" ] && [ "$9" != "SSP2" ]; then
    music0="$9"
    music1="$9"
    music2="$9"
fi

if [ "${10}" != "" ]; then
    music0="${10}"
    music1="${10}"
    music2="${10}"
fi

if [ "$1" == "IAFW" ] && [ "${11}" != "" ] && [ "$7" == "SSP2" ]; then # Cater for SSP2 FW
    music2="${11}"
else
    echo -e "LPE_script ERROR: Please enter SSP2 file"
fi


# =====================================================================
# FUNCTION DECLARATION

# Function to handle search & replacement of specific paterns in the results.
# Necessary function for convert_to_csv()
function replace_line() {
    if [ "$1" != "" ] && [ "$2" != "" ]; then

        file_name=$1 # File name or location
        pattern=$2 # Search pattern can be anything unique that identifies the line
        phrase=$3 # Phrase to replace in the line
        replace=$4 # Substitution string

        ls $file_name
        if [ $? -eq 0 ]; then
        cp $file_name $file_name.bk

        ls $file_name.temp > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "$file_name.temp exists. Please remove or rename it."
        else
        # Find line & pattern to be replaced line by line
            while read line
            do
                if [[ $line=~$pattern ]]; then
                    echo ${line//$phrase/$replace} >> $file_name.temp
                else
                    echo -e "$line\n" >> $file_name.temp
                fi
            done < $file_name

            cp -f $file_name.temp $file_name
            rm -f $file_name.temp

            echo -e "replace_line process complete"
        fi
        else
        echo -e "$file_name not found."
        fi

    else

        echo -e "replace_line.sh error: Please check parameters!"

    fi
}

# Function to filter results to isolate aplay & arecord processes only 
# final manual calculation & sanity check.
function convert_to_csv() {
    # replace_line $1 "," "" > /dev/null
    # replace_line $1 "top - " "," > /dev/null
    # replace_line $1 "Cpu(s): " "," > /dev/null
    # replace_line $1 "\%us" "," > /dev/null
    # replace_line $1 "\%sy" "," > /dev/null
    # replace_line $1 "\%ni" "," > /dev/null
    # replace_line $1 "\%id" "," > /dev/null
    # replace_line $1 "\%wa" "," > /dev/null
    # replace_line $1 "\%hi" "," > /dev/null
    # replace_line $1 "\%si" "," > /dev/null
    # replace_line $1 "\%st" "," > /dev/null
    # replace_line $1 " up " ",,,,,,,," > /dev/null
    # replace_line $1 " 0.0 " ",,,,,,,," > /dev/null
    # replace_line $1 " 0.1 " ",,,,,,,," > /dev/null
    # replace_line $1 " arecord" ",arecord" > /dev/null
    # replace_line $1 " aplay" ",aplay" > /dev/null
    # replace_line $1 " irq/26-i2s_ssp0" ",irq/26-i2s_ssp0" > /dev/null
    # replace_line $1 " irq/27-i2s_ssp1" ",irq/27-i2s_ssp1" > /dev/null
    # replace_line $1 " irq/28-i2s_ssp2" ",irq/28-i2s_ssp2" > /dev/null
    # replace_line $1 " irq/29-intel_ss" ",irq/29-intel_ss" > /dev/null
    # replace_line $1 " S " "," > /dev/null
    # replace_line $1 " R " "," > /dev/null
    # replace_line $1 " D " "," > /dev/null
    # replace_line $1 " " "" > /dev/null
    
    replace_line $1 "," "," "" > /dev/null
    replace_line $1 "-\ " "-\ " "-,\ ,\ ," > /dev/null
    replace_line $1 "-,," "\ " ",," > /dev/null
    replace_line $1 "\%us" "\%us" "" > /dev/null
    replace_line $1 "\%sy" "\%sy" "," > /dev/null
    replace_line $1 "\%id" "\%id" ",," > /dev/null
    replace_line $1 "\ " "\ " "," > /dev/null
    replace_line $1 "root," "root," "" > /dev/null
    replace_line $1 "\%st" ",," "," > /dev/null
    
    cat $1 >> $1_final.csv
    echo -e "$1 Conversion done!"
}


# =====================================================================
# THIS PORTION ONWARDS IS FOR EXECUTION AFTER ALL THE VARIABLES ARE SET

# Double check that no aplay or arecord is running
# Disable this feature to allow the script to be used as single port playback
#pkill -x aplay 
#pkill -x arecord

# TEST MODE HEADER - TEST MODE PARAMETER SET & TEST PRE-SETUP
if [ "$6" != "" ] && [ "$6" == "performance" ]; then
    loop=1
    dur=300 # Test duration for performance data collection. Default is 300sec.
    (top -b -d 5 | awk '/load average/ {n=300} {if (n-- > 0) {print}}' > /home/lpe_cpu_$5_$7''$8''$9_$2''$3''$4.csv) &
    sleep 5
    
elif [ "$6" != "" ] && [ "$6" == "stress" ]; then
    loop=200

elif [ "$6" != "" ] && [ "$6" == "swap" ]; then
    dur=20

    ls /root/ | grep SWAP_LOG_TEMP > /dev/null
    if [ $? -eq 1 ]; then # Creat /root/SWAP_LOG_TEMP if file does not exist
        echo -e "swap_play_count 0" > /root/SWAP_LOG_TEMP
        echo -e "swap_play_flag 1" >> /root/SWAP_LOG_TEMP
        # Add line into profile to auto start script
        cp -f /etc/profile /etc/profile.temp.bk
        
        echo -e "\ncheck=0" >> /etc/profile
        echo -e "max_play_count=$max_swap_play_count" >> /etc/profile
        echo -e "dmesg | grep 'EXT4-fs (sda1):'" >> /etc/profile
        echo -e "check=\$((check+\$?))" >> /etc/profile
        echo -e "dmesg | grep 'EXT4-fs (sda1):'" >> /etc/profile
        echo -e "check=\$((check+\$?))" >> /etc/profile
        echo -e "dmesg | grep 'EXT4-fs (sda1):'" >> /etc/profile
        echo -e "check=\$((check+\$?))" >> /etc/profile
        echo -e "while [ \$check -ne 0 ]; do" >> /etc/profile
        echo -e "    sleep 2" >> /etc/profile
        echo -e "    check=0" >> /etc/profile
        echo -e "    dmesg | grep 'EXT4-fs (sda1):'" >> /etc/profile
        echo -e "    check=\$((check+\$?))" >> /etc/profile
        echo -e "    dmesg | grep 'EXT4-fs (sda1):'" >> /etc/profile
        echo -e "    check=\$((check+\$?))" >> /etc/profile
        echo -e "    dmesg | grep 'EXT4-fs (sda1):'" >> /etc/profile
        echo -e "    check=\$((check+\$?))" >> /etc/profile
        echo -e "done" >> /etc/profile
        echo -e "play_count=\`cat /root/SWAP_LOG_TEMP | grep swap_play_count | awk '{print\$3}'\`" >> /etc/profile
        echo -e "ps aux | grep -v grep | grep 'LPE_script'" >> /etc/profile
        echo -e "if [ \$? -ne 0 ]; then" >> /etc/profile
        echo -e "    sleep 2" >> /etc/profile
        echo -e "    bash /home/Music/LPE_script3.sh "$1" "$2" "$3" "$4" "$5" swap "$7" "$8" "$9 "&" >> /etc/profile
        echo -e "fi" >> /etc/profile
        sync
    fi
    
    ls $directory | grep $file0 > /dev/null
    check0=$?
    ls $directory | grep $file1 > /dev/null
    check1=$?
    ls $directory | grep $file2 > /dev/null
    check2=$?
    
    if [ $check0 -eq 1 ] || [ $check1 -eq 1 ] || [ $check2 -eq 1 ]; then
        
        mount /dev/sdb1 /media
        
        ls $directory | grep $file0 > /dev/null
        check0=$?
        ls $directory | grep $file1 > /dev/null
        check1=$?
        ls $directory | grep $file2 > /dev/null
        check2=$?
        
        if [ $check0 -eq 1 ] || [ $check1 -eq 1 ] || [ $check2 -eq 1 ]; then
            echo -e "Unable to locate audio files. Script terminated..."
            kill_id=`ps aux | grep -v grep | grep '$0' | awk '{print$3}' > /dev/null`
            kill -SIGTERM $kill_id
        fi
    fi
    
    # Buffer to check that LPE driver is loaded
    
    lspci -k | grep 'Intel LPE Audio' > /dev/null
    while [ $? -ne 0 ]; do
        sleep 2
        lspci -k | grep 'Intel LPE Audio' > /dev/null
    done
    
    # Read count from /root/SWAP_LOG_TEMP
    swap_play_count=`cat /root/SWAP_LOG_TEMP | grep swap_play_count | awk '{print$3}'`
    swap_play_flag=`cat /root/SWAP_LOG_TEMP | grep swap_play_flag | awk '{print$3}'`
    # Lines to make the recording filename numerically incremental
    record_file1=$2"_swap_"$((swap_play_count+1))
    record_file2=$3"_swap_"$((swap_play_count+1))
    record_file3=$4"_swap_"$((swap_play_count+1))
    
elif [ "$6" != "" ] && [ "$6" == "auto" ]; then

    record_file1=$2
    record_file2=$3
    record_file3=$4
else
    record_file1=$2
    record_file2=$3
    record_file3=$4
fi


# APLAY CLUSTER
if [ "$5" == "aplay" ] || [ "$5" == "arecord_aplay" ]; then
    if ([ "$7" == "SSP0" ] || [ "$8" == "SSP0" ] || [ "$9" == "SSP0" ]) || [ "$6" == "" ]; then
        echo "(aplay -D $plugin_0 $music0) &"
        (aplay -D $plugin_0 $music0) &
    fi
    if ([ "$7" == "SSP1" ] || [ "$8" == "SSP1" ] || [ "$9" == "SSP1" ]) || [ "$6" == "" ]; then
        echo "(aplay -D $plugin_1 $music1) &"
        (aplay -D $plugin_1 $music1) &
    fi
    if ([ "$7" == "SSP2" ] || [ "$8" == "SSP2" ] || [ "$9" == "SSP2" ]) || [ "$6" == "" ]; then
        if [ "$test_mode" == "IAFW" ]; then
            echo "(aplay -D $hw2 $music2) &"
            (aplay -D $hw2 $music2) &
        elif [ "$test_mode" == "IA" ]; then
            echo "(aplay -D $plugin_2 $music2) &"
            (aplay -D $plugin_2 $music2) &
        fi
    fi
fi

# ARECORD CLUSTER
if [ "$5" == "arecord" ] || [ "$5" == "arecord_aplay" ]; then
    if ([ "$7" == "SSP0" ] || [ "$8" == "SSP0" ] || [ "$9" == "SSP0" ]) || [ "$6" == "" ]; then
        (arecord -D $hw0 -f$bit0 -r $freq -c $rc0 -d $dur /home/SSP0_$record_file1.wav) &
    fi
    if ([ "$7" == "SSP1" ] || [ "$8" == "SSP1" ] || [ "$9" == "SSP1" ]) || [ "$6" == "" ]; then
        (arecord -D $hw1 -f$bit1 -r $freq -c $rc1 -d $dur /home/SSP1_$record_file2.wav) &
    fi
    
    if ([ "$7" == "SSP2" ] || [ "$8" == "SSP2" ] || [ "$9" == "SSP2" ]) || [ "$6" == "" ]; then
        if [ "$test_mode" == "IAFW" ]; then
            (arecord -D hw:0,1 -fS16_LE -r $freq -c $rc2 -d $dur /home/SSP2_$record_file3.wav) &
        elif [ "$test_mode" == "IA" ]; then
            (arecord -D $hw2 -f$bit2 -r $freq -c $rc2 -d $dur /home/SSP2_$record_file3.wav) &
        fi
    fi
fi

# ARECORD PIPE APLAY CLUSTER
if [ "$5" == "pipe" ]; then 
    if ([ "$7" == "SSP0" ] || [ "$8" == "SSP0" ] || [ "$9" == "SSP0" ]) || [ "$6" == "" ]; then
        (arecord -D $hw0 -f$bit0 -r $freq -c $rc0 | aplay -D $plugin_0) &
    fi
    if ([ "$7" == "SSP1" ] || [ "$8" == "SSP1" ] || [ "$9" == "SSP1" ]) || [ "$6" == "" ]; then
        (arecord -D $hw1 -f$bit1 -r $freq -c $rc1 | aplay -D $plugin_1) &
    fi
    
    if ([ "$7" == "SSP2" ] || [ "$8" == "SSP2" ] || [ "$9" == "SSP2" ]) || [ "$6" == "" ]; then
        if [ "$test_mode" == "IAFW" ]; then
            (arecord -D hw:0,1 -fS16_LE -r $freq -c $rc2 | aplay -D $hw2) &
        elif [ "$test_mode" == "IA" ]; then
            (arecord -D $hw2 -f$bit2 -r $freq -c $rc2 | aplay -D $plugin_2) &
        fi
    fi
fi

# TEST MODE FOOTER - TERMINATE TEST MODES & CLEANUP PROCEDURE
if [ "$6" != "" ] && [ "$6" == "performance" ]; then
    sleep $dur
    pkill -SIGTERM -x aplay
    pkill -SIGTERM -x arecord
    sleep 10
    pkill -SIGTERM -x top
    sleep 5
    
    filter="Cpu\\|average\\|aplay\\|arecord"
    
    if ([ "$7" == "SSP0" ] || [ "$8" == "SSP0" ] || [ "$9" == "SSP0" ]) || [ "$6" == "" ]; then
        filter=$filter"\\|irq/26-i2s_ssp0"
    fi
    if ([ "$7" == "SSP1" ] || [ "$8" == "SSP1" ] || [ "$9" == "SSP1" ]) || [ "$6" == "" ]; then
        filter=$filter"\\|irq/27-i2s_ssp1"
    fi
    if ([ "$7" == "SSP2" ] || [ "$8" == "SSP2" ] || [ "$9" == "SSP2" ]) || [ "$6" == "" ]; then
        if [ "$test_mode" == "IAFW" ]; then
            filter=$filter"\\|irq/29-intel_ss"
        elif [ "$test_mode" == "IA" ]; then
            filter=$filter"\\|irq/28-i2s_ssp2"
        fi
    fi
    
    echo $filter # debug use
    
    cat /home/lpe_cpu_$5_$7''$8''$9_$2''$3''$4.csv | grep $filter | awk '{print $2, $3, $5, $9, $12}' > /home/lpe_cpu_$5_$7''$8''$9_$2''$3''$4.txt
    
    convert_to_csv /home/lpe_cpu_$5_$7''$8''$9_$2''$3''$4.txt

elif [ "$6" != "" ] && [ "$6" == "swap" ]; then
    sleep $((dur+2))
    
    # Buffer to check that recording has completed before rebooting
    ps aux | grep -v 'grep\|LPE_script3' | grep 'arecord' > /dev/null
    while [ $? -eq 0 ]; do
       sleep $buffer
       ps aux | grep -v 'grep\|LPE_script3' | grep "arecord"
    done
    
    if [ "$swap_play_count" == "$max_swap_play_count" ] || [ "$swap_play_flag" == "0" ]; then
        rm -f /root/SWAP_LOG_TEMP
        rm -f /etc/profile # Make sure there's no conflict for the next step
        mv -f /etc/profile.temp.bk /etc/profile
        pkill -SIGTERM -x aplay
        pkill -SIGTERM -x arecord
        #pkill -SIGTERM -x bash
        pkill -SIGTERM -x "bash /home/Music/LPE_script3.sh"
        echo -e "\n==================== LPE CHANNEL SWAP TEST COMPLETE!!! ===================="
        date
        sync
        
    else
        # Update /root/SWAP_LOG_TEMP
        echo -e "swap_play_count "$((swap_play_count+1)) > /root/SWAP_LOG_TEMP
        cat /root/SWAP_LOG_TEMP
        echo -e "swap_play_flag "$swap_play_flag >> /root/SWAP_LOG_TEMP
        sync
        
        #pkill -SIGTERM -x aplay
        #pkill -SIGTERM -x arecord
        #pkill -SIGTERM -x "bash /home/Music/LPE_script3.sh"
        
        pkill -x aplay
        pkill -x arecord
        
        sleep 10
        reboot
    fi
fi
