#!/bin/bash

BUILD1=android
BUILD2=linux-x64
BUILD3=linux-x86

TOPDIR=`pwd`
COPYDIR=test_apps

OPTION_0=$0
OPTION_1=$1

echo "This script will copy out the binaries for <builds> from i2c,spi,can,uart"
echo "into $TOPDIR/$OPTION_1"
echo "Usage : $OPTION_0 [$BUILD1 | $BUILD2 | $BUILD3]"
echo " "

if [[ $OPTION_1 == $BUILD1 || $OPTION_1 == $BUILD2 || $OPTION_1 == $BUILD3 ]]; then
 rm -rf "$TOPDIR/$OPTION_1"
 cd $TOPDIR
 echo " cp -r $TOPDIR/i2c/bin/$OPTION_1/ $TOPDIR"
 cp -a "$TOPDIR/i2c/bin/$OPTION_1/" "$TOPDIR"
 echo " cp -r $TOPDIR/spi/bin/$OPTION_1/ $TOPDIR"
 cp -r "$TOPDIR/spi/bin/$OPTION_1/" "$TOPDIR"
 echo " cp -r $TOPDIR/can/bin/$OPTION_1/ $TOPDIR"
 cp -r "$TOPDIR/can/bin/$OPTION_1/" "$TOPDIR"
 echo " cp -r $TOPDIR/uart/bin/$OPTION_1/ $TOPDIR"
 cp -r "$TOPDIR/uart/bin/$OPTION_1/" "$TOPDIR" 
 echo " cp $TOPDIR/spiEEPROM_script" "$TOPDIR/$OPTION_1"
 cp "$TOPDIR/spiEEPROM_script" "$TOPDIR/$OPTION_1"
 shift 1
else
 echo "Invalid Option. Retry with $OPTION_0 [$BUILD1 | $BUILD2 | $BUILD3]"
 exit
fi
