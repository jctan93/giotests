#!/usr/bin/python

import sys
import os
import re
import subprocess
import argparse
import os.path
import shutil
import time

#Run command ~ python tpmtest_compare.py -t testcase_numberinapp.log

#parameters
script_name = str(sys.argv[0])
usage="This program gets the output of the cat file and compare it with the input keyword. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-t', help='test_name/run_all')
args = parser.parse_args()

if args.t is not None:
    test_log = args.t
else:
    print "Argument missing for Test Name..Exiting the Script with Error !"
    sys.exit(1)
    
print "CHECKING ALL VARIABLES ---------------------------------------------------------------------- \n"
print "test_log : " + test_log + "\n"

def log_fnc(string_to_save, test_log):
    os.system('echo ' + string_to_save + ' >> ' + test_log )

def check_log():

    verdict="PASS"

    open_log=open(test_log)
    for aline in open_log:
        if re.search('FAILED', aline):
            verdict="FAIL"
   
    if verdict=="FAIL":
        print "Test {0} is {1} found FAILED in log! \n".format(str(test_log.split('.',0)), verdict )
        msg_log = "Test " + str(test_log.split('.',0)) + " is " + verdict + "found FAILED in log"
    else:
        print "Test {0} is {1}! \n".format(str(test_log.split('.',0)), verdict )
        msg_log = "Test " + str(test_log.split('.',0)) + " is " + verdict

    log_fnc(msg_log,test_log)
    log_fnc(" ",test_log)
    print "Search Done !! ----------------------------------------------------------------- \n"
    return verdict
        
def main ():
    verdict = check_log()
    if verdict == "PASS":
        print "\nFINAL VERDICT: Test PASS!!"
        sys.exit(0)
    else:
        print "\nFINAL VERDICT: Test FAIL!!"
        sys.exit(1)
  
#main
if __name__ == "__main__":
    main ()