#!/bin/bash

set -x

#echo 'Acquire::http::Proxy "http://proxy-png.intel.com:911";' > /etc/apt/apt.conf
#if [ $? -eq 0 ]; then
#	lava-test-case acquire-proxy --result pass
#else
#	lava-test-case acquire-proxy --result fail
#fi
#gcc -s -Wall -Wstrict-prototypes rtc/rtctest.c -o rtctest
#gcc -s -Wall -Wstrict-prototypes rtc/rtc_cmos_test.c -o rtc_cmos_test

#./rtctest
#./rtc_cmos_test

#python gui_startup.py
#python siv_test_collateral/siv_val-io-test-scripts/system/rtc_gio.py -i $sut_ip -t check_driver

chmod +x ./siv_test_collateral/siv_val-io-test-apps/system/lpc.sh
./siv_test_collateral/siv_val-io-test-apps/system/lpc.sh

