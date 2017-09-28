import sys, os, re, time, argparse, string, common
from datetime import date, datetime
from GenericCommand import *
from types import *

m="multiple"
s="single"
test_case = ['ls', 'cat', 'dmesg', 'chk_bios_setting']
flag_verdict = []

usage="This program saerch for keyword in dmesg.If Keyword found, it will prompt PASS.\n"
script_name = str(sys.argv[0])
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-i', help='SUT IP')
parser.add_argument('-k', help='Keyword to Search')
parser.add_argument('-c', help='case[dmesg/lspci/lsusb]')
parser.add_argument('-sub_op', help='Sub Operation')
args = parser.parse_args()

if args.i is not None:
	dev_1_ip = args.i
if args.c is not None:
	case = args.c
	if args.sub_op is not None:
		sub_operation = args.sub_op
	else:
		sub_operation = ""
if args.k is not None:  
	search = args.k
	if search == "all":
		search = ['device','export','npwm','power','subsystem','uevent','unexport']

if case in test_case:
	log = "/" + case + sub_operation + '.log'
else:
	print "Invalid case. Use either 'dmesg' , 'lspci','lsusb', 'lsusb', 'lsdev', 'lspci-k', 'catsys', 'catmmc', 'lssys', 'lsmod', 'cat' , 'lspwm' "
	sys.exit(1)

dut = GenericCommand()
dut.login(dev_1_ip)

def test_print(case,cat_out):
	verdict = "Empty"
	
	print "----------------------------------------------------------------------------"
	print "SEARCH_KEYWORD : " + str(search)
	print "SEARCH_USING : " + case
	print "SEARCH_LOG : " + log
	print "----------------------------------------------------------------------------"
	time.sleep(3)
	splitter = re.compile("\n")
	read_list = splitter.split(cat_out)
	i = 0
	for line in read_list:
		if isinstance(search,basestring):
			if re.search(search ,line):
				print "Keyword Found : " + line
				flag_verdict.append("True")
		else:
			if line in search:
				print "Keywords Found : " + str(search[i])
				flag_verdict.append("True")
				i+=1
	if (flag_verdict[1:] == flag_verdict[:-1]) and ("True" in flag_verdict[:]):
	  verdict = "PASS"
	else:
	  verdict = "FAIL"
	
	print " TEST VERDICT : " + verdict
	return verdict

def main():
	dut.execute("rm -f " + log)
	if case == "dmesg":
		command = case
	elif case == "chk_bios_setting":
		command = "[ -d /sys/firmware/efi ] && echo UEFI || echo NON_UEFI"
	elif case == "ls":
		if sub_operation == "dev":
			command = case + " /dev/"
		elif sub_operation == "pwm":
			command = case + " /sys/class/pwm/"
		elif sub_operation == "pwmchip":
			command = case + " /sys/class/pwm/*"
		elif sub_operation == "pci":
			command = case + "pci -nn"
		elif sub_operation == "pci_advance":
			command = case + "pci -k"
		elif sub_operation == "guc_firmware_integration":
			command = case + " /lib/firmware/i915"
		else:
			command = case + sub_operation
	elif case == "cat":
		if sub_operation == "gpio":
			command = case + " /sys/kernel/debug/gpio"
		elif sub_operation == "mmc":
			command = case + " /sys/kernel/debug/mmc*/ios"
		elif sub_operation == "thermal":
			command = case + " /lib/modules/$(uname -r)/modules.builtin"
		elif sub_operation == "system_init":
			command = case + " /proc/1/comm"
	
	cat_out = dut.execute(command)
	verdict = test_print(case, cat_out)
	dut.execute("rm -f " + log)
	if verdict == "PASS":
		print "\nFINAL VERDICT: Test PASS !!"
		sys.exit(0)
	else:
		print "\nFINAL VERDICT: Test FAIL!!"
		sys.exit(1)
		
main()




