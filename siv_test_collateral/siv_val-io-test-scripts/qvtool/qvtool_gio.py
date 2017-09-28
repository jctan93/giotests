import os, re, sys, json, time, argparse, datetime, glob
from ssh_util import *

test_case_key_name = {'QVTool-F001-M':'QVTool_F001_M','QVTool-F002-M':'QVTool_F002_M'}
script_name = str(sys.argv[0])
usage = "QVTool Test Script"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-thm_ip', help='THM IP')
parser.add_argument('-test_case', help='Test Case ID')
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip
if args.thm_ip is not None:
	thm_ip = args.thm_ip
if args.test_case is not None:
	test_case = args.test_case

ssh_agent = ssh_com(sut_ip)
ssh_agent.setpub(sshpass="")
ssh_thm = ssh_com(thm_ip)
ssh_thm.setpub(sshpass="bxtroot")

def QVTool_F001_M():
	if "iqvlinux" not in ssh_agent.ssh_exec("lsmod | grep -i iqv", verbose=False):
		print "Install iqvlinux.ko"
		ssh_agent.ssh_exec("cd /lib/modules/$(uname -r)/kernel/drivers/net/; insmod iqvlinux.ko", verbose=False)
		verdict = True
	else:
		print "iqvlinux module had preloaded"
		verdict = False
	return verdict

def QVTool_F002_M():
	if "iqvlinux" in ssh_agent.ssh_exec("lsmod | grep -i iqv", verbose=False):
		print "iqvlinux driver had loaded"
		verbose = True
	else:
		print "iqvlinux driver had not loaded"
		verbose = False
	return verdict

def main():
	print "\n=========================== " + test_case_key_name[test_case] + " Function ======================================="
	verdict = eval(test_case_key_name[test_case])()
	if verdict:
		print "Final Test Verdict : PASS"
		sys.exit(0)
	else:
		print "Final Test Verdict : FAIL"
		sys.exit(1)