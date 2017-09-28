import os, re, sys, json, time, argparse
from ssh_util import *

test_case_key_name = {'x11_display':'x11_display_info', 'wayland_display':'wayland_display_info'}

script_name = str(sys.argv[0])
usage = "GFX Display Test Script mainly for grep info"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-test_case', help='Test Case')
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip

if args.test_case is not None:
	test_case = args.test_case
	
ssh_agent = ssh_com(sut_ip)
ssh_agent.setpub(sshpass="")

def x11_display_info():
	if "X Protocol Version 11" in ssh_agent.ssh_exec("Xorg -version",verbose=False):
		print "X11 Found"
		verdict = True
	else:
		print "X11 Not Found"
		verdict = False
	return verdict

def wayland_display_info():
	print "Export the Wayland settings"
	ssh_agent.ssh_exec("export XDG_RUNTIME_DIR=/tmp; unset DISPLAY; weston --tty=2 &", verbose=False)
	time.sleep(10)
	print "Checking weston information"
	if ssh_agent.ssh_exec("weston-info", verbose=False) != "":
		print "Wayland does show the information"
		verdict = True
	else:
		print "Wayland does not show the information"
		verdict = False
	print "Kill weston process"
	ssh_agent.ssh_exec("killall weston", verbose=False)
	
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

main()