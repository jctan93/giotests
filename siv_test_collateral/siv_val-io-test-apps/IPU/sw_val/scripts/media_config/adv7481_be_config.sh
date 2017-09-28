#!/bin/bash

FORMAT=$1
RESOLUTION=$2
INTERLACED=$3

if [ "$FORMAT" = "RGB565" ]; then
	SUBDEV_FMT="RGB16"
    PIXEL_FORMAT="V4L2_PIX_FMT_XRGB32"
elif [ "$FORMAT" = "RGB24" ]; then
	SUBDEV_FMT="RGB24"
    PIXEL_FORMAT="V4L2_PIX_FMT_XBGR32"
elif [ "$FORMAT" = "UYVY" ]; then
	SUBDEV_FMT="UYVY"
elif [ "$FORMAT" = "YUYV" ]; then
	SUBDEV_FMT="YUYV"
else
	SUBDEV_FMT="UYVY"
fi

if [ "$INTERLACED" = "true" ]; then
	FIELD="=ALTERNATE"
fi

chmod +x /home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -r -v

/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -V "\"Intel IPU4 CSI-2 0\":0 [fmt:$SUBDEV_FMT$FIELD/${RESOLUTION}]" -v
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -V "\"Intel IPU4 CSI2 BE SOC\":0 [fmt:$SUBDEV_FMT$FIELD/${RESOLUTION}]"  -v
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -V "\"adv7481 pixel array 2-00e0\":0 [fmt:$SUBDEV_FMT$FIELD/1920x1080]"  -v
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -V "\"adv7481 binner 2-00e0\":0 [fmt:$SUBDEV_FMT$FIELD/1920x1080]"  -v
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -V "\"adv7481 binner 2-00e0\":0 [compose:(0,0)/${RESOLUTION}]"  -v
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -V "\"adv7481 binner 2-00e0\":1 [fmt:$SUBDEV_FMT$FIELD/${RESOLUTION}]"  -v

/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -l "\"adv7481 pixel array 2-00e0\":0 -> \"adv7481 binner 2-00e0\":0[1]"  -v
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -l "\"adv7481 binner 2-00e0\":1 -> \"Intel IPU4 CSI-2 0\":0[1]"  -v
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -l "\"Intel IPU4 CSI-2 0\":1 -> \"Intel IPU4 CSI2 BE SOC\":0[5]"  -v
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -l "\"Intel IPU4 CSI2 BE SOC\":8 -> \"Intel IPU4 BE SOC capture 0\":0[5]"  -v

DEV_NAME=`/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -e "Intel IPU4 BE SOC capture 0"`

. /home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/scripts/tools/mondello_control.sh
#yavta --data-prefix -u -c5 -n5 -I -s${RESOLUTION} -F -f XBGR32 /dev/video14
#vec2raw_linux_x64 frame-000001.bin 1920 1080 grbg8_1920_1080.bin
