import os, re, sys, argparse
#from subprocess import *
from ssh_util import *

iosf_directory = "/sys/kernel/debug/"

script_name = str(sys.argv[0])
usage = "IOSF Test"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-pf', help='Platform [bxt]', default="bxt")
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip
if args.pf is not None:
	platform = args.pf
	if platform == "bxt":
		sbi_directory = iosf_directory + "sbi_apl/"

ssh_agent = ssh_com(sut_ip)

if ssh_agent.ssh_exec("ls -l " + sbi_directory):
	before_modified = ssh_agent.ssh_exec("cat "+ sbi_directory +"data")
	ssh_agent.ssh_exec("echo 6 > "+ sbi_directory +"opcode")
	ssh_agent.ssh_exec("echo 0x500 > "+ sbi_directory +"register_offset")
	ssh_agent.ssh_exec("echo 0xc0 > "+ sbi_directory +"port_address")
	ssh_agent.ssh_exec("echo 1 > "+ sbi_directory +"commit")
	after_modified = ssh_agent.ssh_exec("cat "+ sbi_directory +"data")

if after_modified != "0x00000000":
    print "IOSF Successfully Changed Value"
    sys.exit(0)
else:
    print "IOSF Failed Changed Value"
    sys.exit(1)