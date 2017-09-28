# Description: This script handles the LPE Kernal & Firmware swapping between the different configurations.
# Author: Loh Suat Hoon

# Update 2014-03-07: Added function to record latest kernel version to force kernel to change to desired
# configuration despite current kernel not available.

# Update 2014-05-08: Added condition to check if new image is available. Else Fail verdict.

import sys
import subprocess
import re
import time
import calendar
from datetime import date
import argparse
import GenericCommand


'''Setup SUT for LPE automation testing.
    - Download BzImage daily according to today's date or image directly.
    - Download Firmware daily according to today's date or package directly. 
    - Update BzImage, Firmware and kernel param with each configuration mode. 
'''

def n_date():
    '''Format and return today date.'''
    today = date.today()
    day = str(today.day)
    month = str(today.month)
    year = str(today.year)

    if(len(day)==1):
        day = "0" + day
    if(len(month)==1):
        month = "0" + month

    actualDate = year +"-" + month + "-" + day

    return actualDate

def local_exe(cmd):
    '''Execute command and return standard output.'''
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print str(stdout)
    return str(stdout)

def reboot_chk(dut_IP):
    '''Trace on DUT after reboot and check for bzImage status'''
    dut1 = GenericCommand.GenericCommand()
    host_found = False
    boot_time = 0
    kenel_ver = ""

    while boot_time < 3:
        status = dut1.pingalive(dut_IP, timeout=144)

        if status:
            print "BzImgUpdate.py: Host Found: %s" % dut_IP
            host_found = True
            break
        else:
            boot_time += 1
    else:
        print "BzImgUpdate.py: Host unable to Startup"
        return False
        
    # if host_found:
        # dut1.login(dut_IP)
        # kenel_ver = dut1.execute("uname -a")
        # today = date.today()
        # month_day = calendar.month_abbr[today.month] + " " + str(today.day)
        # if re.search(month_day, kenel_ver):
            # print "Correct BzImage Loaded!"
            # return True
        # else:
            # return False
            
    return True

    
# [MAIN SCRIPT]
test_verdict = True
date_now = n_date()
img_name = "bzImage_LPE_" + date_now
fw_pkg = "LPE_FIRMWARE_" + date_now + ".tar.bz2"
fw_list = {'i2s_master':'fw_sst_0f28.bin-i2s_master',
            'i2s_slave':'fw_sst_0f28.bin-i2s_slave',
            'tdm_master':'fw_sst_0f28.bin-tdm_master',
            'tdm_slave':'fw_sst_0f28.bin-tdm_slave'}

parser = argparse.ArgumentParser(prog="BzImage Update Script", description="Swap kernel and LPE firmware for different configuration")
parser.add_argument("--ip", action="store", help="SUT IP address", default=None)
parser.add_argument("--imglink", action="store", help="BzImage URL Link", default=None)
parser.add_argument("--fwlink", action="store", help="Firmware URL Link", default=None)
parser.add_argument("--img", action="store", help="BzImage Package, If not specified will take latest image", default=None)
parser.add_argument("--fw", action="store", help="Firmware Package, If not specified will take latest firmware", default=None)
parser.add_argument("--mode", action="store", choices=['i2s_master', 'i2s_slave', 'tdm_master', 'tdm_slave'], help="Firmware mode", default="i2s_master")

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(2)

args = parser.parse_args()

dut_IP = args.ip
img_url = args.imglink
fw_url = args.fwlink
fw_mode = args.mode # is actually clock mode. This is a recycled variable

if args.img is not None:
    img_name = args.img
    
if args.fw is not None:
    fw_pkg = args.fw
    

# Login to DUT
dut1 = GenericCommand.GenericCommand()
dut1.login(dut_IP)
#dut1.execute("rm -f /root/Image")
#dut1.execute("mkdir /root/Image")
    
# Check for BzImage
print "BzImgUpdate.py: Searching for %s" % img_name
dut1.execute("rm -f /root/Image/index.html*") # Remove old index.html
dut1.execute("rm -f /root/Image/bzImage*") # Remove previous downloaded bzImage
print "BzImgUpdate.py: URL: %s" % img_url
dut1.execute("wget -P /root/Image --no-proxy %s" % img_url) # Please note that the slash is added in the parameter when the script is executed
ls_img = dut1.execute("cat /root/Image/index.html")

if re.search(img_name, ls_img):
    print "BzImgUpdate.py: New Image Found: %s" % img_name
    img_is_new = True
else:
    print "BzImgUpdate.py: No New Image Today. BzImage Will Not Update."
    #print "LPE Test run will be based on previous BzImage."
    #print "This duplicate test run will be consider as INVALID."
    test_verdict = False
    img_is_new = False
        
# Download BzImage
if test_verdict:
    print "BzImgUpdate.py: Downloading %s from %s" % (img_name,img_url)
    dut1.execute("wget -P /root/Image --no-proxy %s%s" % (img_url,img_name))
    dut1.execute("cp /root/Image/%s /boot/bzImage_LPE" % img_name)
    dut1.execute("echo %s > /root/Image/latest_img" % img_name) # 2014-03-07, record the name of the latest image
    status = dut1.execute("diff /root/Image/%s /boot/bzImage_LPE" % img_name)

    # if status:
        # print "BzImage Failed To Change!"
        # test_verdict = False
    # else:
        # print "BzImage Changed Successfully!"
        
else: # 2014-03-07, Henri: to force Image update
    img_name = dut1.execute("cat /root/Image/latest_img") # Get the name of the last image
    dut1.execute("wget -P /root/Image --no-proxy %s%s" % (img_url,img_name))
    dut1.execute("cp /root/Image/%s /boot/bzImage_LPE" % img_name)
    print "BzImgUpdate.py: No new image found!! Using %s" % img_name
    status = dut1.execute("diff /root/Image/%s /boot/bzImage_LPE" % img_name)

if status:
    print "BzImgUpdate.py: BzImage Failed To Change!"
    test_verdict = False
else:
    print "BzImgUpdate.py: BzImage Changed Successfully!"
    test_verdict = True
# 2014-03-07, Henri: End of edited block     
     
# Download and Extract Firmware
if test_verdict:
    dut1.execute("rm -f /root/Image/index.html*") # Remove old index.html from bzImage checking
    dut1.execute("rm -f /root/Image/LPE_FIRMWARE*") # Remove previously downloaded FW package
    dut1.execute("wget -P /root/Image --no-proxy %s" % fw_url)
    ls_fw = dut1.execute("cat /root/Image/index.html")

    if re.search(fw_pkg, ls_fw):
        print "BzImgUpdate.py: New Firmware Found: %s" % fw_pkg
        dut1.execute("echo %s > /root/Image/latest_fw" % fw_pkg) # 2014-03-07, Henri: to force Image update
        print "BzImgUpdate.py: Download %s" % fw_pkg
        # dut1.execute("wget -P /root/Image --no-proxy %s%s" % (fw_url,fw_pkg))
        # print "Extract %s to /lib/firmware" % fw_pkg
        # dut1.execute("tar -xvf /root/Image/%s -C /lib/firmware/" % fw_pkg)
    else:
        fw_pkg = dut1.execute("cat /root/Image/latest_fw")
        print("BzImgUpdate.py: No New Firmware. Using %s" % fw_pkg)
        
    dut1.execute("wget -P /root/Image --no-proxy %s%s" % (fw_url,fw_pkg))
    print "BzImgUpdate.py: Extract %s to /lib/firmware" % fw_pkg
    dut1.execute("tar -xvf /root/Image/%s -C /lib/firmware/" % fw_pkg)
    # 2014-03-07, Henri: End of edited block

# Modify Kernel Parameters
if test_verdict:
    
    # This portion added by Henri
    # Send replace_line.sh script to SUT
    if dut1.timefiletrace("/root/replace_line.sh") == False:
        dut1.timefiletransfer("/root/replace_line.sh","/root/replace_line.sh")
        print "Sending replace_line.sh script to SUT"
        dut1.execute("chmod +x /root/replace_line.sh")
    
    # Replace the specific line in the boot loader to switch between 2 channel or 8 channel
    print "BzImgUpdate.py: Executing replace_line.sh..."
    if fw_mode == "i2s_master" or fw_mode == "i2s_slave":
        if dut1.timefiletrace("/boot/loader/entries/tizen-kernel.conf"):
            dut1.execute("bash /root/replace_line.sh /boot/loader/entries/tizen-kernel.conf snd_soc_sst_platform.useMultiChannels=8 snd_soc_sst_platform.useMultiChannels=2")
        else:
            # mount Fedora EFI partition
            dut1.execute("mount /dev/sda4 /media; ls /media/efi/boot/grub.cfg; echo -n $?")
            dut1.execute("bash /root/replace_line.sh /media/efi/boot/grub.cfg snd_soc_sst_platform.useMultiChannels=8 snd_soc_sst_platform.useMultiChannels=2")
            dut1.execute("umount /media;")
    else:
        if dut1.timefiletrace("/boot/loader/entries/tizen-kernel.conf"):
            dut1.execute("bash /root/replace_line.sh /boot/loader/entries/tizen-kernel.conf snd_soc_sst_platform.useMultiChannels=2 snd_soc_sst_platform.useMultiChannels=8")
        else:
            # mount Fedora EFI partition
            dut1.execute("mount /dev/sda4 /media; ls /media/efi/boot/grub.cfg; echo -n $?")
            dut1.execute("bash /root/replace_line.sh /media/efi/boot/grub.cfg snd_soc_sst_platform.useMultiChannels=2 snd_soc_sst_platform.useMultiChannels=8")
    # End of alteration
    
    # Change Firmware
    print "Change firmware to %s mode" % fw_mode
    dut1.execute("cp /lib/firmware/%s /lib/firmware/fw_sst_0f28.bin" % fw_list[fw_mode])
    status = dut1.execute("diff /lib/firmware/%s /lib/firmware/fw_sst_0f28.bin" % fw_list[fw_mode])
    
    if status:
        print "BzImgUpdate.py: Firmware Failed To Change!"
        test_verdict = False
    else:
        print "BzImgUpdate.py: Firmware Changed Successfully!"
        print "BzImgUpdate.py: Reboot System Now. Wait for 1 minute to allow SUT boot up."
        dut1.timeexecute("reboot")

        time.sleep(60)

        test_verdict = reboot_chk(dut_IP)
    
else:
    print "BzImgUpdate.py: Skip Firmware as test verdict returns FALSE."
    
# Get final verdict
if test_verdict and img_is_new:
    print "Verdict: PASS!"
    sys.exit(0)
else:
    if not img_is_new:
        print "BzImgUpdate.py: New kernel not available!"
    print "Verdict: FAIL!"
    sys.exit(1)
