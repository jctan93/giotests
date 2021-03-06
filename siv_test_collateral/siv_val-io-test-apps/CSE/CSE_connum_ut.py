#!/usr/bin/python

import sys
import os
import re
import subprocess
import argparse
import os.path
import shutil
import time
import difflib
from subprocess import call
#
# how to use  the script : Run python <script name> -t <test name>
#variables
log_dir = "/home/CSE_RESULT/"
my_log = "/home/CSE_CONSOLE/"
search_keyword = "OK"

#parameters
script_name = str(sys.argv[0])
usage="This program gets the output of the cat file and compare it with the input keyword. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-t', help='test_name (connum_ut)')
args = parser.parse_args()

if args.t is not None:
    test_name = args.t
else:
    print "Argument missing for Test Name..vi Exiting the Script with Error !"
    sys.exit(1)
    
print "CHECKING ALL VARIABLES ---------------------------------------------------------------------- \n"
print "test_name : " + test_name


		
def connum_ut(test_name):
    if test_name == "connum_ut":   
        print "TESTING FOR : ---------- " + test_name + " ---------- "
        test_to_execute1 = "dmesg -c"
        test_to_execute2 = "python /home/siv_test_collateral/siv_val-io-test-apps/CSE/connum_ut.py &> /home/CSE_CONSOLE/connum_ut_console.log"
        test_to_execute3 = "dmesg > /home/CSE_CONSOLE/connum_ut_dmesg.log"
        print "Executing : " + test_name
        print "Command : " + test_to_execute2
        os.system(test_to_execute1)
        os.system(test_to_execute2)
        os.system(test_to_execute3)
        print "Test is executed successfully ---------------------------------- \n"
    else: 
        print "Test is Fail"

def check():
    result = "FAIL"
    log_data1=open("/home/CSE_CONSOLE/connum_ut_console.log")
    for log_data in log_data1:
        if re.search(search_keyword,log_data):
            result = "PASS"
            break
    print "[Debug]return in check_log : " + result
    print "----------------------------------------------------------------------------"
    return result 


def verdict_fnc(verdict):
    print "[Debug]: " + verdict
    if verdict == "PASS":
        print "\nFINAL VERDICT: Test PASS!!"
        sys.exit(0)
    else:
        print "\nFINAL VERDICT: Test FAIL!!"
        sys.exit(1)

    
def main (test_name):

        os.system("mkdir /home/CSE_CONSOLE/")
        #os.system("echo 0 >/home/CSE_CONSOLE/connum_ut_console.log")
        connum_ut(test_name)
        if test_name == "connum_ut":
                final_result = check()
                verdict_fnc(final_result)

        
        print "Time After execution : " + time.strftime("%H:%M:%S")
        sys.exit(0)   
        
#main
if __name__ == "__main__":
    main (test_name)