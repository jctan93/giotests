import os, re, sys, json, time, argparse, datetime, multiprocessing, StringIO, GenericCommand
from ssh_util import *

thm_ip = sys.argv[1]
sut_ip = sys.argv[2]
master_id = sys.argv[3]
slave_id = sys.argv[4]

ssh_agent = ssh_com(sut_ip)
ssh_agent.setpub(sshpass="")
ssh_minno = ssh_com(thm_ip)
ssh_minno.setpub(sshpass="bxtroot")

multiple_splitter = re.compile("->|../|\n")

master_command = "ls -l /dev/disk/by-id | grep -i " + str(master_id) + " | grep -v part"
master_label_wo_dev = str(multiple_splitter.split(ssh_agent.ssh_exec(master_command))[-1])
master_label = "/dev/" + master_label_wo_dev
slave_command = "ls -l /dev/disk/by-id | grep -i " + str(slave_id) + " | grep -v part"
slave_label = "/dev/" + multiple_splitter.split(ssh_agent.ssh_exec(slave_command))[-1]

if "mmc" in master_label:
    master_label += "p"
if "mmc" in slave_label:
    slave_label += "p"
print "\nMaster Label : " + master_label + "\nSlave Label : " + slave_label + "\n"

if ssh_agent.ssh_exec("ls / | grep MASTER"):
	print "Master booted"
	ssh_agent.ssh_exec("mount "+ master_label +"1 /media && rm -rf /media/BOOT_MARKER") 
	ssh_agent.ssh_exec("sync")
	ssh_agent.ssh_exec("mount "+ slave_label +"1 /mnt && touch /mnt/BOOT_MARKER")
	ssh_agent.ssh_exec("sync")
	ssh_agent.ssh_exec("reboot")
	# ssh_minno.ssh_exec("python ~/BXT_Daily_Automation/GPIO.py 338 5")
	# ssh_minno.ssh_exec("python ~/BXT_Daily_Automation/GPIO.py 338 1")
	# time.sleep(20)
else:
	print "Slave booted"
	ssh_agent.ssh_exec("mount " + master_label + "1 /media && touch /media/BOOT_MARKER")
	ssh_agent.ssh_exec("sync")
	ssh_agent.ssh_exec("mount " + slave_label + "1 /mnt && rm -rf /mnt/BOOT_MARKER")
	ssh_agent.ssh_exec("sync")
	ssh_agent.ssh_exec("reboot")
	# ssh_minno.ssh_exec("python ~/BXT_Daily_Automation/GPIO.py 338 5")
	# ssh_minno.ssh_exec("python ~/BXT_Daily_Automation/GPIO.py 338 1")
	# time.sleep(20)
