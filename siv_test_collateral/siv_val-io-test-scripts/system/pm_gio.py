import sys, os, re, time, argparse, GenericCommand, string, common
from datetime import date, datetime
from ssh_util import *

#Default parameters
sut_ip = "172.30.248.212"
gcs_port = "2300"
gpio_test_script_location = "/root/BXT_Daily_Automation/GPIO.py"
gpio_pin = "338"
test_config_location = "/home/siv_test_collateral/siv_val-io-test-scripts/system/"

script_name = str(sys.argv[0])
usage = "This is power management test"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-thm_ip', help='THM IP')
parser.add_argument('-slave', help='Slave Disk ID')
parser.add_argument('-op', help='Operation [mem, wake_up, onS0, shutdown, S4, RS4, reboot]')
parser.add_argument('-os', help='Operating System [yocto, tizen]', default="yocto")
args = parser.parse_args()

pat = re.compile('SLAVE_DEV|SLAVE_SWAP')
splitter_x = re.compile("x")
splitter_next = re.compile("\n")
multiple_splitter = re.compile("->|../|\n|-")

if args.sut_ip is not None:
	sut_ip = args.sut_ip
	
if args.thm_ip is not None:
	thm_ip = args.thm_ip
	
if args.slave is not None:
	slave_id = args.slave
	
if args.op is not None:
	operation = args.op

ssh_agent = ssh_com(sut_ip)
ssh_agent.setpub(sshpass="")
ssh_minno = ssh_com(thm_ip)
ssh_minno.setpub(sshpass="bxtroot")

if args.os is not None:
	operating_system = args.os
	if operating_system == "yocto":
		kernel_version = multiple_splitter.split(ssh_agent.ssh_exec("uname -r")[0])
		if kernel_version >= "4.9": # for kernel version 4.9
			grub_location = "/mnt/loader/entries/"
			default_grub_naming = "boot.conf"
		elif kernel_version < "4.9": # for kernel version 4.1
			grub_location = "/mnt/EFI/BOOT/"
			default_grub_naming = "grub.cfg"
	elif operating_system == "tizen":
		grub_location = "/boot/loader/entries/"
		default_grub_naming = "default.conf" 


slave_command = "ls -l /dev/disk/by-id | grep -i " + str(slave_id) + " | grep -v part"
slave_label_wo_dev = str(multiple_splitter.split(ssh_agent.ssh_exec(slave_command))[-1])
slave_label = "/dev/" + slave_label_wo_dev
slave_disk_identifier = ssh_agent.ssh_exec("fdisk -l " + slave_label + " | grep -i identifier")
slave_partuuid = splitter_x.split(slave_disk_identifier)[-1]

def power_on_S0():
	print "==== Power On From S0 / Hard Reboot Test ====\n"
	ssh_minno.ssh_exec("python " + gpio_test_script_location + " " + gpio_pin + " 5")
	ssh_minno.ssh_exec("python " + gpio_test_script_location + " " + gpio_pin + " 1")
	time.sleep(5)
	if ssh_agent.chk_con(timeout=120): 
		print "Wake Up From S0 Test: PASS"
		sys.exit(0)
	else: 
		print "Wake Up From S0 Test: FAIL"
		sys.exit(1)

def shutdown():
	print "==== Normal Shutdown Test ====\n"
	ssh_agent.ssh_exec("shutdown now")
	time.sleep(20)
	if not ssh_agent.chk_con(timeout=10):
		ssh_minno.ssh_exec("python " + gpio_test_script_location + " " + gpio_pin + " 1")
		# time.sleep(30)
		if ssh_agent.chk_con(timeout=120):
			print "Normal Shutdown Test : PASS"
			sys.exit(0)
	else:
		print "Normal Shutdown Test : FAIL"
		sys.exit(1)
		
def hibernation():
	print "==== Hibernation (S4) Test ====\n"
	ssh_agent.ssh_exec("mount " + slave_label + "1 /mnt")
	ssh_agent.ssh_exec("sed -i '$s/$/ resume=\/dev\/" + slave_label_wo_dev + "3 resumedelay=3/' " + grub_location + default_grub_naming + "; sync")
	ssh_agent.ssh_exec("reboot")
	time.sleep(5)
	if ssh_agent.chk_con(timeout=120):
		ssh_agent.ssh_exec("echo disk > /sys/power/state &")
		time.sleep(20)
		if not ssh_agent.chk_con(timeout=10):
			time.sleep(5)
			ssh_minno.ssh_exec("python " + gpio_test_script_location + " " + gpio_pin + " 1")
			if ssh_agent.chk_con():
				print "Hibernation Test : PASS"
				sys.exit(0)
		else:
			print "Hibernation Test : FAIL"
			sys.exit(1)
	else:
		print "Connection not established"
		sys.exit(1)
		
def resume_hibernation():
	print "==== Resume From Hibernation Test ====\n"
	if ssh_agent.chk_con():
		print "Resume From Hibernation Test : PASS"
		ssh_agent.ssh_exec("mount " + slave_label + "1 /mnt")
		ssh_agent.ssh_exec("sed -i 's/resume=\/dev\/" + slave_label_wo_dev + "3 resumedelay=3//' " + grub_location + default_grub_naming + "; sync")
		ssh_agent.ssh_exec("reboot")
		time.sleep(10)
		if ssh_agent.chk_con():
			print "Connection established"
			sys.exit(0)
		else:
			print "Connection fail established"
			sys.exit(1)
	else:
		print "Resume From Hibernation Test : FAIL"
		sys.exit(1)

def sleep():
	print "==== Sleep (S3) Test ===="
	ssh_agent.ssh_exec("echo mem > /sys/power/state &")
	time.sleep(20)
	if not ssh_agent.chk_con(timeout=60):
		print "Sleep Test : PASS"
		ssh_minno.ssh_exec("python " + gpio_test_script_location + " " + gpio_pin + " 1")
		if ssh_agent.chk_con(sut_ip):
			print "Connection established"
			sys.exit(0)
	else:
		print "Sleep Test : FAIL"
		sys.exit(1)

def wake_up():
	print "==== Wake Up From Sleep (S3) Test ====\n"
	if ssh_agent.chk_con(timeout=10):
		print "Wake Up From Sleep Test : PASS"
		sys.exit(0)
	else:
		print "Wake Up From Sleep Test : FAIL"
		sys.exit(1)

def reboot():
	print "==== Soft Reboot Test ===="
	ssh_agent.ssh_exec("reboot")
	time.sleep(10)
	if ssh_agent.chk_con(timeout=60):
		print "Soft Reboot Test : PASS"
		sys.exit(0)
	else:
		print "Soft Reboot Test : FAIL"
		sys.exit(1)
		
def check_ip_connection():
	if ssh_agent.chk_con(timeout=60):
		print "On board Connection Test : PASS"
		sys.exit(0)
	else:
		print "On board Connection Test : FAIL"
		sys.exit(1)
		
def main():
	if operation == "onS0":
		power_on_S0() # Test Case : SYS-PM002-M
	elif operation == "shutdown":
		shutdown() # Test Case : SYS-PM003-M
	elif operation == "S4":
		hibernation() # Test Case : SYS-PM006-M
	elif operation == "RS4": # Resume from S4 
		resume_hibernation() # Test Case : SYS-PM007-M
	elif operation == "mem":
		sleep() # Test Case : SYS-PM002-M
	elif operation == "wake_up":
		wake_up() # Test Case : SYS-PM002-M
	elif operation == "reboot":
		reboot() # Test Case : FSP-F004-M
	elif operation == "chk_ip_connection":
		check_ip_connection() # Test Case : FSP-F006-M
		
main()