#!/bin/bash

chmod +x /home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl
/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -r -v
DEV_NAME=`/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/bin/media-ctl -e "Intel IPU4 TPG 0"`