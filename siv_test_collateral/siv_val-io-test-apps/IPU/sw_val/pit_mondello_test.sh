#!/bin/bash

# Gstreamer Test cases
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_YUY2_1920x1080_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_YUY2_1280x720_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_YUY2_720x576_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_YUY2_640x480_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_YUY2_1920x1080_Interlaced_Deinterlace
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_YUY2_720x480_Interlaced_Deinterlace
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_YUY2_720x576_Interlaced_Deinterlace

sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB24_1920x1080_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB24_1280x720_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB24_720x576_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB24_640x480_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB24_1920x1080_Interlaced_Deinterlace
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB24_720x576_Interlaced_Deinterlace
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB24_720x480_Interlaced_Deinterlace

sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB565_1920x1080_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB565_1280x720_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB565_720x576_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB565_640x480_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB565_1920x1080_Interlaced_Deinterlace
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB565_720x576_Interlaced_Deinterlace
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_Display_RGB565_720x480_Interlaced_Deinterlace

# Gstreamer DMA buffer import test cases
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_DMABufImport_YUY2_720x576_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_DMABufImport_YUY2_640x480_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_DMABufImport_YUY2_1280x720_Progressive
sh /home/root/sw_val/scripts/gst_test.sh CAMERA_GST_PRI_VF_DMABufImport_YUY2_1920x1080_Progressive

# IPU DSS test cases
gst-launch-1.0 icamerasrc device-name=imx185 ! video/x-raw, format=NV12,width=1920,height=1080 ! vaapipostproc ! vaapisink
gst-launch-1.0 icamerasrc num-buffers=50 device-name=imx185 ! 'video/x-raw,format=NV12,width=1920,height=1080' !  vaapipostproc ! vaapih264enc ! mp4mux ! filesink location=test.mp4
gst-launch-1.0 icamerasrc device-name=imx185 num-buffers=100 ! video/x-raw,format=NV12,width=1920,height=1080 ! multifilesink location=imx185_NV12_1920_1080%d.nv12   
gst-launch-1.0 icamerasrc device-name=imx185 ! 'video/x-raw,format=NV12,width=1920,height=1080'  ! fakesink

# MSDK test cases
gst-launch-1.0 icamerasrc device-name=mondello num-buffers=100 io-mode=3 ! video/x-raw,format=UYVY,width=1920, height=1080 ! mfxvpp ! mfxsink