#!/bin/bash
chmod +x /home/root/sw_val/bin/media-ctl
/home/root/sw_val/bin/media-ctl -r -v
DEV_NAME=`/home/root/sw_val/bin/media-ctl -e "Intel IPU4 CSI-2 1"`