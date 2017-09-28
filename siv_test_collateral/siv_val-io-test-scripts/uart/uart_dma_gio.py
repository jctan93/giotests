#Created by: Quek, Zhen Han Deric (11576007)
#Description: To test HSUART DMA Support
#Dependencies and pre-requisites: N/A
#Last modified by: Loo, Willam (11604964)
#Last modified date: 27 OCT 2016
#Modification description: remove logfile feature and add some checking.
#Thanks to Andrew and William for pointing that out.


import os
import sys
import re
from ssh_util import *

ssh_sut = ssh_com(sys.argv[1])

def execute(command):
    status = ssh_sut.ssh_exec(command)
    return status

def grab_dma_msg():
	multiple_splitter = re.compile(",|\n")
	dmesg_list = execute("dmesg -t | grep -i DMA | grep -i tty")
	cleanup()
	if ("ttyS2 - failed to request DMAttyS3 - failed to request DMA" in dmesg_list):
		return True   
	else:
		return False

def result_checker(status):
    if status:
        print "HSUART DMA Support Test : PASS"
        sys.exit(0)
    else:
        print "HSUART DMA Support Test : FAIL"
        sys.exit(1)

def cleanup():
    print "Cleaning"
    execute("sync; echo 1 > /proc/sys/vm/drop_caches")

def main():
	print "----- Checking HSUART DMA Support -----"
	
	#grab_dma_msg()
	execute("echo abc > /dev/ttyS0")
	execute("echo abc > /dev/ttyS1")
	execute("echo abc > /dev/ttyS2")
	execute("echo abc > /dev/ttyS3")
	# status = grab_dma_msg()
	result_checker(grab_dma_msg())

main()
