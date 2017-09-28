import os, re, sys, json, time, argparse, datetime, multiprocessing, StringIO
from ssh_util import *

# hpet_testapp
test_config_location = "/home/siv_test_collateral/siv_val-io-test-scripts/system/"
test_app_location = "/home/siv_test_collateral/siv_val-io-test-apps/hpet/"

# regular expression part
pat = re.compile('SLAVE_DEV')
splitter_x = re.compile("x")
splitter_next = re.compile("\n")
splitter_colon = re.compile(":")
splitter_space = re.compile(" ")
splitter_equal = re.compile("=")
multiple_splitter = re.compile("->|../|\n|-")

script_name = str(sys.argv[0])
usage = "This is HPET Automation script"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-thm_ip', help='THM IP')
parser.add_argument('-op', help='Operation ["verify_timer", "power_consumption"]')
parser.add_argument('-slave', help='Slave Disk ID')
parser.add_argument('-os', help='Operating System [yocto, tizen ]', default="yocto")
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip
if args.thm_ip is not None:
	thm_ip = args.thm_ip
	thm_password = "bxtroot"
if args.op is not None:
	operation = args.op
if args.slave is not None:
	slave_id = args.slave
	
ssh_agent = ssh_com(sut_ip)
ssh_agent.setpub(sshpass="")
ssh_minno = ssh_com(thm_ip)
ssh_minno.setpub(sshpass=thm_password)

if args.os is not None:
	operating_system = args.os
	if operating_system == "yocto":
		kernel_version = multiple_splitter.split(ssh_agent.ssh_exec("uname -r")[0])
		if kernel_version >= "4.9": # for kernel version 4.9
			grub_location = "/mnt/loader/entries/"
			default_grub_naming = "boot.conf"
			power_consumption_command = "sed -i '$s/$/ clocksource=hpet/' "
		elif kernel_version < "4.9": # for kernel version 4.1
			grub_location = "/mnt/EFI/BOOT/"
			default_grub_naming = "grub.cfg"
			power_consumption_command = "sed -i '/ipc/s/$/ clocksource=hpet/' "
	elif operating_system == "tizen":
		grub_location = "/boot/loader/entries/"
		default_grub_naming = "default.conf" 

slave_command = "ls -l /dev/disk/by-id | grep -i " + str(slave_id) + " | grep -v part"
slave_label = "/dev/" + str(multiple_splitter.split(ssh_agent.ssh_exec(slave_command))[-1])
slave_disk_identifier = splitter_space.split(splitter_colon.split(splitter_next.split(ssh_agent.ssh_exec("fdisk -l " + slave_label + " | grep -i 'identifier'"))[0])[1])[1]

if "dos" in ssh_agent.ssh_exec("fdisk -l " + slave_label + " | grep -i 'disklabel'"):
	slave_partuuid = splitter_x.split(slave_disk_identifier)[-1]
	flag = "dos"
elif "gpt" in ssh_agent.ssh_exec("fdisk -l " + slave_label + " | grep -i 'disklabel'"):
	slave_partuuid = splitter_space.split(splitter_colon.split(slave_disk_identifier)[1])[1]
	flag = "gpt"

def main():
	if operation == "verify_timer": 
		result = splitter_space.split(splitter_equal.split(ssh_agent.ssh_exec(test_app_location + "hpet-example poll /dev/hpet 200 2"))[-1])[-1]
		print "Expired Time Output from test app : " + result
		if result != "0x000":
			print "Test Verdict Pass"
			sys.exit(0)
		else:
			print "Test Verdict Fail"
			sys.exit(1)
	elif operation == "power_consumption":
		if operating_system == "yocto":
			ssh_agent.ssh_exec("mount " + slave_label + "1 /mnt")
		elif operating_system == "tizen":
			ssh_agent.ssh_exec("mount " + slave_label + "1 /boot")
			
		# before changing kernel: "sed -i '/ipc/s/$/ clocksource=hpet/' "
		ssh_agent.ssh_exec(power_consumption_command + grub_location + default_grub_naming + "; sync")
		ssh_agent.ssh_exec("reboot")
		time.sleep(10)
		if ssh_agent.chk_con():
			if "hpet" in ssh_agent.ssh_exec("cat /sys/devices/system/clocksource/clocksource0/current_clocksource"):
				if operating_system == "yocto":
					ssh_agent.ssh_exec("mount " + slave_label + "1 /mnt")
				elif operating_system == "tizen":
					ssh_agent.ssh_exec("mount " + slave_label + "1 /boot")
				ssh_agent.ssh_exec("sed -i 's/clocksource=hpet//' " + grub_location + default_grub_naming + "; sync")
				ssh_agent.ssh_exec("reboot")
				time.sleep(10)
				if ssh_agent.chk_con():
					print "Connection established"
				else:
					print "Connection aborted"
				print "SYS-HPET001-M PASS"
			else:
				print "SYS-HPET001-M FAIL"
	else:
		print "Invalid operation entered"
		sys.exit(1)

main()