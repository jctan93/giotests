import sys, os, re, argparse, time
from ssh_util import *

#	parameter definition
dal_script_location = "/home/siv_test_collateral/siv_val-io-test-apps/DAL/"
# test_case_key_name = {}
test_case_key_name = {'DAL_security-F022-M-001':'Opening Intel SD session', 'DAL_security-F022-M-002':'Installing the production BIST applet',
					  'DAL_security-F022-M-003':'Closing the Intel SD session', 'DAL_security-F022-M-004':'Initializing JHI',
					  'DAL_security-F022-M-005':'Creating a session', 'DAL_security-F022-M-006':'Running the Compare Buffer test',
					  'DAL_security-F022-M-007':'Making sure the Compare Buffer test passed', 'DAL_security-F022-M-008':'Running the Echo test',
					  'DAL_security-F022-M-009':'Making sure the Echo test passed', 'DAL_security-F022-M-010':'Closing the session',
					  'DAL_security-F022-M-011':'Uninstalling', 'all':'Print Bist Output'}
script_name = str(sys.argv[0])
usage="This program gets the output of the cat file and compare it with the input keyword. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-test_case', help='Test Case')
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip
if args.test_case is not None and args.test_case in test_case_key_name:
	test_case = str(args.test_case)
else:
	print "Invalid test case."
	sys.exit(1)

print "TEST CASE : " + test_case

ssh_agent = ssh_com(sut_ip)
ssh_agent.setpub(sshpass="")

def search_result():
	if "Success" in ssh_agent.ssh_exec("bist | grep -i '" + test_case_key_name[test_case] + "'"):
		print test_case_key_name[test_case] + " : Success"
		verdict = True
	else:
		print test_case_key_name[test_case] + " : Fail"
		verdict = False
	return verdict

def main():
	verdict = search_result()
	if verdict == True:
		print "Verdict for " + test_case_key_name[test_case] + ": PASS"
		sys.exit(0)
	else:
		print "Verdict for " + test_case_key_name[test_case] + ": FAIL"
		sys.exit(1)
main()