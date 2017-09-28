import os,sys,subprocess, argparse
from ssh_util import *

tpm_script_location = "/home/siv_test_collateral/siv_val-io-test-apps/tpm/TPM2.0_test_script/"

script_name = str(sys.argv[0])
usage="TPM Test Script"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-p', help='Parameter')
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip
if args.p is not None:
	parameter = args.p
	
def main():
	ssh_agent = ssh_com(sut_ip)
	ssh_agent.setpub(sshpass="")
	ssh_agent.ssh_exec("/usr/sbin/resourcemgr > ~/resourcemgr_log 2>&1 &")
	print "Running TPM Bash Script"
	output = ssh_agent.ssh_exec(tpm_script_location + "tpmtest.sh " + parameter)
	
	if "PASS" in output:
		print "FINAL VERDICT : Test PASS"
		resourcemgr_id = ssh_agent.ssh_exec("pgrep resourcemgr | xargs echo")
		ssh_agent.ssh_exec("kill -9 " + resourcemgr_id)
		sys.exit(0)
	else:
		print "FINAL VERDICT : TEST FAIL"
		sys.exit(1)
	
main()
