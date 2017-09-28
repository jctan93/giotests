import argparse, subprocess, sys

test_case_key_name = {'IPP-F001-M': 'static_library_test','IPP-F002-M': 'dynamic_library_test'}
ipp_test_script_location = "/home/siv_test_collateral/siv_val-io-test-apps/ipp/"
script_name = str(sys.argv[0])
usage = "This is power management test"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-test_case', help='Test Case [IPP-F001-M(static_library_test), IPP-F002-M(dynamic_library_test)]')
args = parser.parse_args()

if args.test_case is not None and args.test_case in test_case_key_name:
	test_case = args.test_case
else:
	print "Invalid test case."
	sys.exit(1)

def execute(cmd):
	proc = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
	(out, err) = proc.communicate()
	return (out, err)

def static_library_test():
	execute(ipp_test_script_location + "build.sh >> " + ipp_test_script_location + test_case + ".log")
	output = execute("cat " + ipp_test_script_location + test_case + ".log")[0]
	print "LOGFILE: \n" + output
	
	if "Static libraries test" in output and "TEST PASSED" in output:
		print "Static Library Test PASS"
		verdict = True
	else:
		print "Static Library Test FAIL"
		verdict = False
	return verdict

def dynamic_library_test():
	execute(ipp_test_script_location + "build.sh >> " + ipp_test_script_location + test_case + ".log")
	output = execute("cat " + ipp_test_script_location + test_case + ".log")[0]
	print "\nLOGFILE: \n" + output
	
	if "Dynamic libraries test" in output and "TEST PASSED" in output:
		print "Dynamic Library Test PASS"
		verdict = True
	else:
		print "Dynamic Library Test FAIL"
		verdict = False
		
	return verdict

def main():
	verdict = eval(test_case_key_name[test_case])()
	print "\n==================== IPP App Test Case Result ==============================="
	print "TEST CASE : " + test_case
	if verdict == True:
		print "Verdict for " + test_case + ": PASS"
		execute("rm -rf " + ipp_test_script_location + test_case + ".log")
		print "=============================================================================="
		sys.exit(0)
	else:
		print "Verdict for " + test_case + ": FAIL"
		print "=============================================================================="
		sys.exit(1)
	
main()