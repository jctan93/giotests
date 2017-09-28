import sys, os, re, time, argparse, string, common
from datetime import date, datetime
from ssh_util import *

gcs_port = "2300"
apps_location = "/home/siv_test_collateral/siv_val-io-test-apps/storage/"
partition_list = [1,2,3,5,6]
flag_verdict = []

multiple_splitter = re.compile("->|../")

script_name = str(sys.argv[0])
usage = "This is pstorage test"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-ip', help='SUT IP')
parser.add_argument('-op', help='Operation [partition, format, mount, copy_across, umount]')
parser.add_argument('-pn', help='Partition Number [2,5]')
parser.add_argument('-ft', help='Format [FAT32, exFAT, ext2, ext3, ext4, vfat]')
parser.add_argument('-dv', help='Device Name')
parser.add_argument('-md', help='Media [USB, SD, SATA]')
args = parser.parse_args()

if args.ip is not None:
	dev_1_ip = args.ip
if args.op is not None:
	operation = args.op
	if operation not in ['partition','format','mount','copy_across','umount']:
		print "Invalid Operation. Please check --help"
		sys.exit(1)
if args.pn is not None:
	if int(args.pn) in [1, 2, 5]:
		partition_number = args.pn
	else:
		print "Test case supports only 2 and 5 partitions."
		sys.exit(1)
if args.ft is not None:
	format = args.ft.lower()
if args.dv is not None:
	device_name = args.dv
if args.md is not None:
	media = args.md

dut_ssh = ssh_com(dev_1_ip)
dut_ssh.setpub(sshpass="")

device_command = "ls -l /dev/disk/by-id | grep -i " + str(device_name) + " | grep -v part"
device_label_wo_dev = str(multiple_splitter.split(dut_ssh.ssh_exec(device_command))[-1])
if device_label_wo_dev != "":
	device_label = "/dev/" + device_label_wo_dev
else:
	print "Device not found. Proceed to exit."
	sys.exit(1)

def create_file():
	create_file_cmd = "dd if=/dev/zero of="+ apps_location +"and.txt count=100 bs=1048576"
	dut_ssh.ssh_exec(create_file_cmd)
	dut_ssh.ssh_exec("sync")
	if dut_ssh.ssh_exec("ls -l " + apps_location + " | grep -i and.txt"):
		print "Create file at " + apps_location + " successfully."
	else:
		print "Create file at " + apps_location + " failed."

def partition(reset_partition_number = "False"):
	global partition_number
	if media == "SD":
		extended_label = "p"
	elif media == "USB" or media == "SATA":
		extended_label = ""

	if reset_partition_number == "True":
		partition_number = 1

	check_capacity_command = "fdisk -l " + device_label + " | grep -w " + device_label + " | awk '{print \$5}'" 
	capacity = dut_ssh.ssh_exec(check_capacity_command)
	each_partition_capacity = int(capacity) / int(partition_number)
	each_partition_capacity_MB = each_partition_capacity / 1048576 - 100

	if int(partition_number) == 1:
		cmd_partition_script = apps_location + "partitions.sh " + device_label + " " + str(partition_number) + " " + str(each_partition_capacity_MB)
	elif int(partition_number) == 2:
		cmd_partition_script = apps_location + "partitions.sh " + device_label + " " + str(partition_number) + " " + str(each_partition_capacity_MB) + " " + str(each_partition_capacity_MB)
	elif int(partition_number) == 5:
		cmd_partition_script = apps_location + "partitions.sh " + device_label + " " + str(partition_number) + " " + str(each_partition_capacity_MB) + " " + str(each_partition_capacity_MB) + " " + str(each_partition_capacity_MB) + " " + str(each_partition_capacity_MB) + " " + str(each_partition_capacity_MB)
	
	dut_ssh.ssh_exec(cmd_partition_script)
	time.sleep(5)
	for i in range(0, int(partition_number)):
		check_partition_command = "fdisk -l " + device_label + " | grep -w " + device_label + extended_label + str(partition_list[i])
		if re.search(device_label + extended_label + str(partition_list[i]), dut_ssh.ssh_exec(check_partition_command)):
			if reset_partition_number != "True":
				print "Partition Found : " + device_label + extended_label + str(partition_list[i])
				flag_verdict.append("True")
		else:
			print "Invalid Partition" + device_label
			flag_verdict.append("False")
	
	if (flag_verdict[1:] == flag_verdict[:-1]) and ("True" in flag_verdict[:]):
		if reset_partition_number != "True":
			print "Partition Test : PASS"
			sys.exit(0)
	else:
		print "Partition Test : FAIL"
		sys.exit(1)


def format_partition():
	if format == "fat32":
		format_cmd = "mkdosfs -F 32 "
		search_keyword = "FAT"
	elif format == "exfat":
		format_cmd = "mkfs.exfat "
		search_keyword = "MBR"
	elif format == "ext2":
		format_cmd = "mkfs.ext2 "
		search_keyword = "ext2"
	elif format == "ext3":
		format_cmd = "mkfs.ext3 "
		search_keyword = "ext3"
	elif format == "ext4":
		format_cmd = "mkfs.ext4 "
		search_keyword = "ext4"
	elif format == "vfat":
		format_cmd = "mkfs.vfat "
		search_keyword = "FAT"
		
	if media == "SD":
		extended_label = "p"
	elif media == "USB" or media == "SATA":
		extended_label = ""
	
	for i in range(0, int(partition_number)):
		format_partition_cmd = format_cmd + device_label + "" + extended_label + "" + str(partition_list[i])
		# print format_partition_cmd
		dut_ssh.ssh_exec(format_partition_cmd)
		check_partition_format_cmd = "file -sL " + device_label + extended_label + str(partition_list[i])
		if re.search(search_keyword, dut_ssh.ssh_exec(check_partition_format_cmd)):
			print device_label + extended_label + str(partition_list[i]) + " successfully formatted to " + format
			flag_verdict.append("True")
		else:
			print device_label + extended_label + str(partition_list[i]) + " fail formatted to " + format
			flag_verdict.append("False")
	
	if (flag_verdict[1:] == flag_verdict[:-1]) and ("True" in flag_verdict[:]):
		print "Format Partition Test : PASS"
		sys.exit(0)
	else:
		print "Format Partition Test : FAIL"
		sys.exit(1)


def mount_partition(copy_across = "False", list_position = ""):
	mount_dir = " /media/"
	if format in ["fat32", "ext2", "ext3", "ext4", "vfat"]:
		mount_cmd = "mount "
	elif format == "exfat":
		mount_cmd = "mount.exfat-fuse "
	else :
		print "Wrong format given"
		sys.exit(1)
	
	if media == "SD":
		extended_label = "p"
	elif media == "USB" or media == "SATA":
		extended_label = ""

	if copy_across == "False":
		for i in range(0, int(partition_number)):
			dut_ssh.ssh_exec("mkdir " + mount_dir + media + str(partition_list[i]))
			mount_partition_cmd = mount_cmd + device_label + extended_label + str(partition_list[i]) + mount_dir + media + str(partition_list[i])
			# print mount_partition_cmd
			dut_ssh.ssh_exec(mount_partition_cmd)
			check_mount_partition_cmd = "df " + device_label + extended_label + str(partition_list[i])
			if re.search(device_label + extended_label + str(partition_list[i]), dut_ssh.ssh_exec(check_mount_partition_cmd)):
				print device_label + extended_label + str(partition_list[i]) + " successfully mounted "
				flag_verdict.append("True")
			else:
				print device_label + extended_label + str(partition_list[i]) + " failed to mounted "
				flag_verdict.append("False")
		
		if (flag_verdict[1:] == flag_verdict[:-1]) and ("True" in flag_verdict[:]):
			print "Mount Partition Test : PASS"
			sys.exit(0)
		else:
			print "Mount Partition Test : FAIL"
			sys.exit(1)
	else :
		print "Mounting Partition"
		mount_partition_cmd = mount_cmd + device_label + extended_label + str(partition_list[list_position]) + mount_dir + media + str(partition_list[list_position])
		dut_ssh.ssh_exec(mount_partition_cmd)


def copy_across():
	create_file()
	mount_dir = " /media/"
	copy_cmd = "cp -r "
	if media == "SD":
		extended_label = "p"
	elif media == "USB" or media == "SATA":
		extended_label = ""
		
	md5_original_file = dut_ssh.ssh_exec("md5sum " + apps_location + "and.txt | awk '{print \$1}'")
	print "Original File Checksum: " + md5_original_file
	for i in range(0, int(partition_number)):
		copy_file_cmd = copy_cmd + apps_location + "and.txt" + mount_dir + media + str(partition_list[i])
		# print copy_file_cmd
		dut_ssh.ssh_exec(copy_file_cmd)
		umount_partition(copy_across = "True", list_position = i)
		mount_partition(copy_across = "True", list_position = i)
		checksum_file = dut_ssh.ssh_exec("md5sum " + mount_dir + media  + str(partition_list[i])+ "/and.txt | awk '{print \$1}'")
		print "Checksum for " + str(mount_dir + media + str(partition_list[i])) + ": " + checksum_file
		if  checksum_file == md5_original_file:
			print "File Found at " + mount_dir + media  + str(partition_list[i]) + "\n"
			flag_verdict.append("True")
		else:
			print "Fail to copy file"
			flag_verdict.append("False")
			
	if (flag_verdict[1:] == flag_verdict[:-1]) and ("True" in flag_verdict[:]):
		print "Removing and.txt from partition"
		dut_ssh.ssh_exec("rm -rf " + mount_dir + media + "*/" + "and.txt")
		print "Read Write Test : PASS"
		sys.exit(0)
	else:
		print "Read Write Test : FAIL"
		sys.exit(1)		
	

def umount_partition(copy_across = "False", list_position = ""):
	mount_dir = " /media/"
	umount_cmd = "umount "
	if media == "SD":
		extended_label = "p"
	elif media == "USB" or media == "SATA":
		extended_label = ""
		
	if copy_across == "False":
		for i in range(0, int(partition_number)):
			umount_partition_cmd = umount_cmd + mount_dir + media + str(partition_list[i])
			# print umount_partition_cmd
			dut_ssh.ssh_exec(umount_partition_cmd)
			check_umount_partition_cmd = "df " + device_label + extended_label + str(partition_list[i])
			if not re.search(device_label + extended_label + str(partition_list[i]), dut_ssh.ssh_exec(check_umount_partition_cmd)):
				print device_label + extended_label + str(partition_list[i]) + " successfully unmounted "
				flag_verdict.append("True")
			else:
				print device_label + extended_label + str(partition_list[i]) + " failed to unmounted "
				flag_verdict.append("False")

		print "Removing and.txt file in " + mount_dir + media
		dut_ssh.ssh_exec("rm -rf " + mount_dir + "*")
		print "Removing " + apps_location +"and.txt"
		dut_ssh.ssh_exec(apps_location +"and.txt")
		if (flag_verdict[1:] == flag_verdict[:-1]) and ("True" in flag_verdict[:]):
			partition(reset_partition_number = "True") # reset partition to one
			print "Un-Mount Partition Test : PASS"
			sys.exit(0)
		else:
			print "Un-Mount Partition Test : FAIL"
			sys.exit(1)
		
	else:
		print "Un-Mounting Partition" + mount_dir + media + str(partition_list[list_position])
		umount_partition_cmd = umount_cmd + mount_dir + media + str(partition_list[list_position])
		# print umount_partition_cmd
		dut_ssh.ssh_exec(umount_partition_cmd)
		 
def main():
	if operation == "partition":
		partition()
	elif operation == "format":
		format_partition()
	elif operation == "mount":
		mount_partition()
	elif operation == "copy_across":
		copy_across()
	elif operation == "umount":
		umount_partition()

main()