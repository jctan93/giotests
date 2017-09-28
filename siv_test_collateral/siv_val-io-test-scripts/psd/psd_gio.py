import argparse
from ssh_util import *

test_case_key_name = {'PSD-GETINFO-F001-M': 'PSD_GETINFO_F001_M','PSD-GETINFO-F002-M': 'PSD_GETINFO_F002_M','PSD-GETINFO-F010-M': 'PSD_GETINFO_F010_M','PSD-GETINFO-F011-M': 'PSD_GETINFO_F011_M','PSD-GETINFO-F012-M': 'PSD_GETINFO_F012_M'}

script_name = str(sys.argv[0])
usage = "This is power management test"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-test_case', help='Test Case [PSD-GETINFO-F001-M, PSD-GETINFO-F002-M, PSD-GETINFO-F010-M, PSD-GETINFO-F011-M, PSD-GETINFO-F012-M]')
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip
if args.test_case is not None and args.test_case in test_case_key_name:
	test_case = args.test_case
else:
	print "Invalid test case."
	sys.exit(1)

ssh_agent = ssh_com(sut_ip)
ssh_agent.setpub(sshpass="")

def PSD_GETINFO_F001_M():
	ssh_agent.ssh_exec("echo -e 'bxtroot\\nbxtroot\\n' | adduser test1")
	
	ssh_temp_agent = ssh_com(sut_ip, user="test1")
	ssh_temp_agent.setpub(sshpass="bxtroot")
	ssh_temp_agent.ssh_exec("/usr/bin/psdapp /sys/firmware/acpi/tables/PSDS >> ~/" + test_case_key_name[test_case] + ".log")
	
	if "Input file is not valid. Please try again" in ssh_temp_agent.ssh_exec("cat ~/" + test_case_key_name[test_case] + ".log"):
		print "Expected input file not valid"
		verdict = True
	else:
		print "Fail to run or privilege problem"
		verdict = False
		
	ssh_agent.ssh_exec("userdel test1")
	return verdict

def PSD_GETINFO_F002_M():
	ssh_agent.ssh_exec("/usr/bin/psdapp /sys/firmware/acpi/tables/PSDS >> ~/" + test_case_key_name[test_case] + ".log")
	if "Input file is not valid. Please try again" not in ssh_agent.ssh_exec("cat ~/" + test_case_key_name[test_case] + ".log"):
		print "PSDS Apps Capable to read PSDS ACPI Table"
		verdict = True
	else:
		print "PSDS Apps NOT Capable to read PSDS ACPI Table"
		verdict = False
	return verdict

def PSD_GETINFO_F010_M():
	ssh_agent.ssh_exec("/usr/bin/psdapp >> ~/" + test_case_key_name[test_case] + ".log")
	if "Correct Usage" in ssh_agent.ssh_exec("cat ~/" + test_case_key_name[test_case] + ".log"):
		print "PSDS Apps Capable to show --help"
		verdict = True
	else:
		print "PSDS Apps NOT Capable to show --help"
		verdict = False
	return verdict

def PSD_GETINFO_F011_M():
	ssh_agent.ssh_exec("/usr/bin/psdapp 1 >> ~/" + test_case_key_name[test_case] + ".log")
	if "Correct Usage" in ssh_agent.ssh_exec("cat ~/" + test_case_key_name[test_case] + ".log"):
		print "PSDS Apps Capable to show --help"
		verdict = True
	else:
		print "PSDS Apps NOT Capable to show --help"
		verdict = False
	return verdict

def PSD_GETINFO_F012_M():
	ssh_agent.ssh_exec("/usr/bin/psdapp 'abcdefg' >> ~/" + test_case_key_name[test_case] + ".log")
	if "Correct Usage" in ssh_agent.ssh_exec("cat ~/" + test_case_key_name[test_case] + ".log"):
		print "PSDS Apps Capable to show --help"
		verdict = True
	else:
		print "PSDS Apps NOT Capable to show --help"
		verdict = False
	return verdict

def main():
	verdict = eval(test_case_key_name[test_case])()
	print "\n==================== PSDS App Test Case Result ==============================="
	print "TEST CASE : " + test_case
	if verdict == True:
		print "Verdict for " + test_case_key_name[test_case] + ": PASS"
		print "=============================================================================="
		sys.exit(0)
	else:
		print "Verdict for " + test_case_key_name[test_case] + ": FAIL"
		print "=============================================================================="
		sys.exit(1)
	
main()