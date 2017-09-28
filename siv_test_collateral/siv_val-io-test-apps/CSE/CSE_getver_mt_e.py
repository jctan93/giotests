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
search_keyword = "Errno"
test_script_location = "/home/siv_test_collateral/siv_val-io-test-apps/CSE/"
#parameters
script_name = str(sys.argv[0])
usage="This program gets the output of the cat file and compare it with the input keyword. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-t', help='test_name (getver_mt_e)')
args = parser.parse_args()

if args.t is not None:
    test_name = args.t
else:
    print "Argument missing for Test Name..vi Exiting the Script with Error !"
    sys.exit(1)
    
print "CHECKING ALL VARIABLES ---------------------------------------------------------------------- \n"
print "test_name : " + test_name


		
def getver_mt_e(test_name):
    if test_name == "getver_mt_e":   
        print "TESTING FOR : ---------- " + test_name + " ---------- "
        test_to_execute1 = "dmesg -c"
        test_to_execute2 = "echo 'Errno' > /home/CSE_CONSOLE/getver_mt_e_console.log"
        test_to_execute3 = "python "+ test_script_location +"getver_mt.py -e &> /home/CSE_CONSOLE/getver_mt_e_console.log"
        test_to_execute4 = "dmesg > /home/CSE_CONSOLE/getver_mt_e_dmesg.log"
        print "Executing : " + test_name
        print "Command : " + test_to_execute2
        os.system(test_to_execute1)
        os.system(test_to_execute2)
        os.system(test_to_execute3)
        os.system(test_to_execute4)
        print "Test is executed successfully ---------------------------------- \n"
    else: 
        print "Test is Fail"

def check():
    result = "PASS"
    log_data1=open("/home/CSE_CONSOLE/getver_mt_e_console.log")
    for log_data in log_data1:
        if re.search(search_keyword,log_data):
            result = "FAIL"
            break
    print "[Debug]return in check_log : " + result
    print "----------------------------------------------------------------------------"
    return result 


def verdict_fnc(verdict):
    print "[Debug]: " + verdict
    if verdict == "FAIL":
        print "\nFINAL VERDICT: Test FAIL!!"
        sys.exit(1)
    else:
        print "\nFINAL VERDICT: Test PASS!!"
        sys.exit(0)

    
def main (test_name):

        os.system("mkdir /home/CSE_CONSOLE/")
        #os.system("echo 0 >/home/CSE_CONSOLE/getver_mt_e_console.log")
        getver_mt_e(test_name)
        if test_name == "getver_mt_e":
                final_result = check()
                verdict_fnc(final_result)

        
        print "Time After execution : " + time.strftime("%H:%M:%S")
        sys.exit(0)   
        
#main
if __name__ == "__main__":
    main (test_name)