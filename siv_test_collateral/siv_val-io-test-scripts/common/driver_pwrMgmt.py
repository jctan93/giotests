##################################################################################################################
# 
# Created by    : Liow, Shi Jie (11569681)
# Description   : This script is for testing driver power management functionality. 
#                   To use this script for projects other than APL-I :
#                      - retune the sleep timers as required
#                      - update GPIO pin that controls USB power
# Dependencies and Pre-requisites : To test USB driver power management, use SATA or eMMC as boot device.
# Last Modified by          : Liow, Shi Jie (11569681)
# Last Modified Date        : 19/Oct/2016
# Modification Description  : Created this script
#
##################################################################################################################

import os
import sys
import time
import subprocess
import re
from GenericCommand import *

dut = GenericCommand()
dut.login(sys.argv[1])

def execute(command, wait=True):
    out = dut.execute(command)
    return out
"""
    if wait is True:
        (out, err) = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    else:
        out = None
        err = None
        subprocess.Popen(command, shell=True)
    if err:
        print "ERROR : " + err
        exit(1)
    else:
        return out    
"""
def pwrStatus_serial(subComponent, fileNode, busNo):
     # only if the default baud rate changes power status too fast
    if subComponent == "uart":
        execute("stty -F " + fileNode + " 50")
        time.sleep(1)
    check = [None] * 3
    check[0] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be suspended
    output = execute("echo 100 > " + fileNode + " &", wait=False)
    time.sleep(0.1) # delay to let drivers change state. Tuned for APL-I, Leaf Hill. Re-tune if necessary for other devices
    check[1] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be active
    time.sleep(2)
    check[2] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be suspended
    check = map(str.strip, check)
    expected = ["suspended", "active", "suspended"]
    print check
    print expected
    if check == expected:
        return True
    else:
        return False

def unmount(fileNode):
    output = execute("cat /proc/mounts | grep " + fileNode)
    if output is not "":
        print fileNode + " is mounted. Unmounting now"
        execute("umount " + fileNode)
        return
    else:
        print fileNode + " is not mounted."
        return
        
def sata_preSetup(sata_fileNode, sata_busNo):
    # setting SATA driver power mgmt to auto
    execute("echo auto > /sys/bus/pci/devices/0000\:00\:" + sata_busNo + "/ata1/host0/target0\:0\:0/0\:0\:0\:0/power/control")
    execute("echo auto > /sys/bus/pci/devices/0000\:00\:" + sata_busNo + "/ata1/power/control")
    execute("echo auto > /sys/bus/pci/devices/0000\:00\:" + sata_busNo + "/power/control")
    # setting suspend delay time to 1 second
    execute("echo 1000 > /sys/bus/pci/devices/0000\:00\:" + sata_busNo + "/ata1/host0/target0\:0\:0/0\:0\:0\:0/power/autosuspend_delay_ms")
    unmount(sata_fileNode)
    time.sleep(2)

def sd_preSetup(sd_fileNode, sd_busNo):
    execute("echo auto > /sys/bus/pci/devices/0000\:00\:" + sd_busNo + "/power/control")
    unmount(sd_fileNode)
    time.sleep(3.5)
    
def pwrStatus_sata_sd(subComponent, fileNode, busNo):
    if subComponent == "sata":
        sata_preSetup(fileNode, busNo)
    elif subComponent == "sd":
        sd_preSetup(fileNode, busNo)
    #elif subComponent == "usb":
    #   print "something"
    #    # usb code goes here
    execute("mkdir ~/pwrMgmt_temp") # create temp dir for mounting
    check = [None] * 3
    check[0] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be suspended
    output = execute("mount " + fileNode + " ~/pwrMgmt_temp")
    time.sleep(0.1)
    check[1] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be active
    time.sleep(3.5)
    check[2] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be suspended
    #cleanup
    execute("umount " + fileNode)
    execute("rm -rf ~/pwrMgmt_temp")
    #results checking
    check = map(str.strip, check)
    expected = ["suspended", "active", "suspended"]
    print check
    print expected
    if check == expected:
        return True
    else:
        return False

def pwrStatus_usb(subComponent, fileNode, busNo):
    # check if usb is the boot device
    bootDriveCheck1 = execute("lsblk | grep /boot")
    bootDriveCheck2 = execute("lsblk | grep /media/realroot")
    print bootDriveCheck1
    print bootDriveCheck2
    if (fileNode[-4:-1] in bootDriveCheck1 or fileNode[-4:-1] in bootDriveCheck2):
        print "USB detected as boot drive. Please clone image to an alternate boot media (SATA or eMMC) to run USB driver power management test."
        exit(1)
    else:
        unmount(fileNode)
        execute("echo auto > /sys/bus/pci/devices/0000\:00\:" + busNo + "/power/control")
        GPIO_PIN = "457" # GPIO_457 is for APL-I. This pin controls power to ALL usb ports. it may change for other projects
        execute("echo " + GPIO_PIN + " > /sys/class/gpio/export")
        execute("echo out > /sys/class/gpio/gpio" + GPIO_PIN + "/direction")
        execute("echo 0 > /sys/class/gpio/gpio" + GPIO_PIN + "/value")
        time.sleep(1)
        check = [None] * 3
        check[0] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be suspended
        execute("echo 1 > /sys/class/gpio/gpio" + GPIO_PIN + "/value") 
        time.sleep(3)
        check[1] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be active
        execute("echo 0 > /sys/class/gpio/gpio" + GPIO_PIN + "/value")
        time.sleep(1)
        check[2] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be suspended
        # cleanup
        execute("echo 1 > /sys/class/gpio/gpio" + GPIO_PIN + "/value")
        execute("echo " + GPIO_PIN + " > /sys/class/gpio/unexport")
        #results checking
        check = map(str.strip, check)
        expected = ["suspended", "active", "suspended"]
        print check
        print expected
        if check == expected:
            return True
        else:
            return False

def pwrStatus_pwm(subComponent, fileNode, busNo):
    pwmPin_no = fileNode[-1]
    pwmchip = "pwmchip0" # APL-I only has one pwmchip (pwmchip0)
    execute("echo " + pwmPin_no + " > /sys/class/pwm/" + pwmchip + "/export") 
    execute("echo auto > /sys/bus/pci/devices/0000\:00\:" + busNo + "/power/control")
    execute("echo 0 > /sys/class/pwm/pwmchip0/" + fileNode + "/enable")
    time.sleep(1)
    check = [None] * 3
    check[0] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be suspended
    execute("echo 1 > /sys/class/pwm/pwmchip0/" + fileNode + "/enable")
    time.sleep(0.1)
    check[1] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be active
    execute("echo 0 > /sys/class/pwm/pwmchip0/" + fileNode + "/enable")
    time.sleep(0.5)
    check[2] = execute("cat " + "/sys/bus/pci/devices/0000\:00\:" + busNo + "/power/runtime_status") # should be suspended
    # cleanup
    execute("echo " + pwmPin_no + " > /sys/class/pwm/" + pwmchip + "/unexport")
    #results checking
    check = map(str.strip, check)
    expected = ["suspended", "active", "suspended"]
    print check
    print expected
    if check == expected:
        return True
    else:
        return False
    
            
def main():
# main code goes here
    if len(sys.argv) is not 5:
        print "This script takes exactly Four (4) inputs.\nUsage: driver_pwrMgmt.py <ip_address> <subcomponent> <file_node | disk_id> <bus_number>\nExample: driver_pwrMgmt.py uart /dev/ttyS1 18.1"
        print "List of supported IO sub-components :\n uart - /dev/ttySX\n i2c - /dev/i2c-X\n spi - /dev/spidevX.Y\n sata - disk_id\n sd - disk_id\n usb - disk_id\n pwm - pwmX"
        exit(1)
    subComponent = sys.argv[2]
    fileNode_diskID = sys.argv[3]
    busNo = sys.argv[4]
    
    if (subComponent == 'uart' or subComponent == 'spi' or subComponent == 'i2c'):
        fileNode = fileNode_diskID
        verdict = pwrStatus_serial(subComponent, fileNode, busNo)
    elif (subComponent == 'sata' or subComponent == 'sd' or subComponent == 'usb'):
        if "/dev" in fileNode_diskID:
            print "File node is not supported for this sub-component. Please obtain unique disk-id.\n Command : # ls /dev/disk/by-id"
            exit(1)
        else: # find which file node the disk-id corresponds to
            diskID = fileNode_diskID
            output = execute("ls -la /dev/disk/by-id | grep " + diskID).split("\n")[0][-3:]
            if subComponent == 'sd':
                output = execute("ls -la /dev/disk/by-id | grep " + diskID).split("\n")[0][-7:] + "p1"
            fileNode = "/dev/" + output
        if subComponent == 'usb':
            verdict = pwrStatus_usb(subComponent, fileNode, busNo)
        else:
            verdict = pwrStatus_sata_sd(subComponent, fileNode, busNo)
    elif (subComponent == 'pwm'):
        fileNode = fileNode_diskID
        verdict = pwrStatus_pwm(subComponent, fileNode, busNo)
    else:
        print "IO Sub-Component '" + subComponent + "' not supported. List of supported IO sub-components :\n uart\n i2c\n spi\n sata\n sd\n usb\n pwm"
        exit(1)
    if verdict is True:
        print "Test Result : PASS"
        exit(0)
    else:
        print "Test Result : FAIL"
        exit(0)
        
    
        

if __name__=="__main__":
    main()

