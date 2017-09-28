#!/bin/bash

REG=0
EXT_REG=0
VALUE=0
REG_WRITE=0
REG_READ=0
DWC_PHY_REG=9300C280

if [ $# -ne 1 ]; then
	echo "usage:"
	echo " source ulpi_read.sh <reg>"
	echo " e.g source ulpg_read.sh 4f"
else

let EXT_FLG=0xc0;
let "REG=0x$1"
let "EXT_REG=$REG&$EXT_FLG"

# Read Action Handled here
echo READ Action Starting....
if [ $EXT_REG = 0 ]; then
echo NORMAL register...
	REG_NEWREGREQ=0x2000000;
	let "REG_REGADDR=(0x3f&$REG)<<16"
	let "REG_WRITE=$REG_NEWREGREQ+$REG_REGADDR"
	REG_WRITE=$(echo ""$REG_WRITE" 16 o p" | dc)
	echo Write 0x$REG_WRITE to DWC PHY VIEWPORT register 0x$DWC_PHY_REG
	./memprobe /dev/mem w $DWC_PHY_REG $REG_WRITE
	usleep 1000
	RESULT=$(./memprobe /dev/mem r $DWC_PHY_REG | awk '{print $NF}')
	echo Read from 0x$DWC_PHY_REG DWC PHY VIEWPORT register is $RESULT
	let "RESULT=((0xff&$RESULT))"
	echo So register value is:
	echo ""$RESULT" 16 o p" | dc
else
	echo EXT register...
	let REG_NEWREGREQ=0x2000000;
	let REG_REGADDR_EXT=0x2f0000;
	let "REG_VCTRL=$REG<<8"
	let "REG_WRITE=$REG_NEWREGREQ+$REG_REGADDR_EXT+$REG_VCTRL"
	REG_WRITE=$(echo ""$REG_WRITE" 16 o p" | dc)
	echo Write 0x$REG_WRITE to DWC PHY VIEWPORT register 0x$DWC_PHY_REG
	./memprobe /dev/mem w $DWC_PHY_REG $REG_WRITE
	usleep 1000
	RESULT=$(./memprobe /dev/mem r $DWC_PHY_REG | awk '{print $NF}')
	echo Read from 0x$DWC_PHY_REG DWC PHY VIEWPORT register is $RESULT
	let "RESULT=((0xff&$RESULT))"
	echo So register value is:
	echo ""$RESULT" 16 o p" | dc
fi
fi
