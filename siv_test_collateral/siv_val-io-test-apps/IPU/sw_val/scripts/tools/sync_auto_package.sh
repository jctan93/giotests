#!/bin/bash

AUTO_PACKAGE_SERVER_IP=10.239.134.238
SERVER_LOCATION="/share/icg_sh_share/AUTO/sw_val"
DUT_LOCATION=/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val

cd /home/root
rm -r ${DUT_LOCATION}
IP_ADDR=`LC_ALL=C ifconfig | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'`
staf $AUTO_PACKAGE_SERVER_IP fs copy DIRECTORY $SERVER_LOCATION TODIRECTORY $DUT_LOCATION TOMACHINE $IP_ADDR RECURSE
chmod +x ${DUT_LOCATION} -R