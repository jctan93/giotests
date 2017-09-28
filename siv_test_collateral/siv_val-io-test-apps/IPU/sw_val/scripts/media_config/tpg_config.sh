#!/bin/sh

format=$1 # SGRBG8
res=$2 #720x576

chmod +x /home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -r -v

/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -V '"Intel IPU4 TPG 0":0 [fmt:'$format'/'$res']' -v
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -l '"Intel IPU4 TPG 0":0 -> "Intel IPU4 TPG 0 capture":0[1]' -v

DEV_NAME=`/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -e "Intel IPU4 TPG 0 capture"`

# yavta -u -n1 --capture=3 -s $res -F -f $format $DEV_NAME

