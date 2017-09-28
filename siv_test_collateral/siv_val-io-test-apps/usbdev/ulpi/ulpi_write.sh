#!/bin/bash

REG=0
EXT_REG=0
VALUE=0
REG_WRITE=0
REG_READ=0
DWC_PHY_REG=9300C280

if [ $# -ne 2 ]; then
	echo "usage:"
	echo " source ulpi_write.h <reg> <value>"
	echo " e.g source ulpg_write.sh 80 7f"
else

let EXT_FLG=0xc0;
let "REG=0x$1"
let "DATA=0x$2"
let "EXT_REG=$REG&$EXT_FLG"

# Read Action Handled here
echo READ Action Starting....
if [ $EXT_REG = 0 ]; then
	echo NORMAL register...
	# parmeters
	let REG_NEWREGREQ=0x2000000;
	let REG_REGWR=0x400000;
	let "REG_REGADDR=(0x3f&$REG)<<16"
	let "REG_DATA=$DATA&0xff"
	let "REG_WRITE=$REG_NEWREGREQ+$REG_REGADDR+$REG_REGWR+$REG_DATA"

	REG_WRITE=$(echo ""$REG_WRITE" 16 o p" | dc)
	echo Write 0x$REG_WRITE to DWC PHY VIEWPORT register 0x$DWC_PHY_REG
	./memprobe /dev/mem w 0x$DWC_PHY_REG 0x$REG_WRITE
	usleep 1000
	RESULT=$(./memprobe /dev/mem r 0x$DWC_PHY_REG)
	echo Read from 0x$DWC_PHY_REG DWC PHY VIEWPORT register is $RESULT
	let "RESULT=((0x1000000&0x$RESULT))"
	if [ $RESULT = 0 ]; then
		echo write action failed.
	else
		echo write action done.
	fi
else
	echo EXT register...
	# parmeters
	let REG_NEWREGREQ=0x2000000;
	let REG_REGADDR_EXT=0x2f0000;
	let REG_REGWR=0x400000;
	let "REG_VCTRL=$REG<<8"
	let "REG_DATA=$DATA&0xff"
	let "REG_WRITE=$REG_NEWREGREQ+$REG_REGADDR_EXT+$REG_VCTRL+$REG_DATA+$REG_REGWR"

	REG_WRITE=$(echo ""$REG_WRITE" 16 o p" | dc)
	echo Write 0x$REG_WRITE to DWC PHY VIEWPORT register 0x$DWC_PHY_REG
	./memprobe /dev/mem w 0x$DWC_PHY_REG 0x$REG_WRITE
	usleep 1000
	RESULT=$(./memprobe /dev/mem r 0x$DWC_PHY_REG | awk '{print $NF}')
	echo Read from 0x$DWC_PHY_REG DWC PHY VIEWPORT register is $RESULT
	let "RESULT=((0x1000000&$RESULT))"
	if [ $RESULT = 0 ]; then
		echo write action failed.
	else
		echo write action done.
	fi
fi
fi
