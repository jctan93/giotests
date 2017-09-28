import os, re, sys, time, argparse
from ssh_util import *

test_app_location = "/home/siv_test_collateral/siv_val-io-test-apps/watchdog/"
# python /home/automation_script/watchdog_gio.py <IP> <option>
script_name = str(sys.argv[0])
usage = "Watchdog test"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-op', help='Option = [check_driver, watchy1, watchy3]')
parser.add_argument('-status', help='Status = [activation, deactivation] -- Apply when watchy1')
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip
else:
	print "-sut_ip missing"
	sys.exit(1)

if args.op is not None:
	option = args.op
	if option == "watchy1":
		if args.status is not None:
			status = args.status
		else:
			print "-status is empty"
			sys.exit(1)
else:
	print "-op missing"
	sys.exit(1)

ssh_agent = ssh_com(sut_ip)

def main():
	if option == "check_driver":
		if ssh_agent.ssh_exec("cat /proc/iomem | grep -i iTCO_wdt") != "" and ssh_agent.ssh_exec("cat /proc/ioports | grep -i iTCO_wdt") != "":
			print "Watchdog driver present"
			sys.exit(0)
		else:
			print "Watchdog driver not present"
			sys.exit(1)
	elif option == "watchy3":
		list_output = ssh_agent.ssh_exec(test_app_location + option)
		time.sleep(60)
		if ssh_agent.chk_con():
			print "WATCHDOG-F004-M PASS"
			sys.exit(0)
		else:
			sys.exit(1)
	elif option == "watchy1":        
		if status == "activation":
			list_output = ssh_agent.ssh_exec(test_app_location + option)
			time.sleep(60)
			if ssh_agent.chk_con():
				print "WATCHDOG-F003-M-001 PASS"
				sys.exit(0)
			else:
				print "WATCHDOG-F003-M-001 FAIL"
				sys.exit(1)
		
		if status == "deactivation":
			ssh_agent.ssh_exec("rmmod iTCO_wdt; rmmod iTCO_vendor_support")
			time.sleep(120)
			if ssh_agent.chk_con():
				ssh_agent.ssh_exec("modprobe iTCO_wdt; modprobe iTCO_vendor_support")
				print "WATCHDOG-F003-M-002 PASS"
				sys.exit(0)
			else: 
				print "WATCHDOG-F003-M-002 FAIL"
				sys.exit(1)
main()
