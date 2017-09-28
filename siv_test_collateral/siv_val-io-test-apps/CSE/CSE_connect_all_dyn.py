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

#parameters
script_name = str(sys.argv[0])
usage="This program gets the output of the cat file and compare it with the input keyword. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-t', help='test_name (conalldyn)')
args = parser.parse_args()


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
search_keyword = "Error"

#parameters
script_name = str(sys.argv[0])
usage="This program gets the output of the cat file and compare it with the input keyword. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-t', help='test_name (connect_all_dyn)')
args = parser.parse_args()

if args.t is not None:
    test_name = args.t
else:
    print "Argument missing for Test Name..vi Exiting the Script with Error !"
    sys.exit(1)
    
print "CHECKING ALL VARIABLES ---------------------------------------------------------------------- \n"
print "test_name : " + test_name


		
def connect_all_dyn(test_name):
    if test_name == "connect_all_dyn":   
        print "TESTING FOR : ---------- " + test_name + " ---------- "
        test_to_execute1 = "dmesg -c"
        test_to_execute2 = "python connect_all_dyn.py &> /home/CSE_CONSOLE/connect_all_dyn_console.log"
        test_to_execute3 = "dmesg > /home/CSE_CONSOLE/connect_all_dyn_dmesg.log"
        print "Executing : " + test_name
        print "Command : " + test_to_execute2
        os.system(test_to_execute1)
        os.system(test_to_execute2)
        os.system(test_to_execute3)
        print "Test is executed successfully ---------------------------------- \n"
    else: 
        print "Test is Fail"

def check():
    result = "PASS"
    log_data1=open("/home/CSE_CONSOLE/connect_all_dyn_console.log")
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
        #os.system("echo 0 >/home/CSE_CONSOLE/connect_all_dyn_console.log")
        connect_all_dyn(test_name)
        if test_name == "connect_all_dyn":
                final_result = check()
                verdict_fnc(final_result)

        
        print "Time After execution : " + time.strftime("%H:%M:%S")
        sys.exit(0)   
        
#main
if __name__ == "__main__":
    main (test_name)
if args.t is not None:
    test_name = args.t
else:
    print "Argument missing for Test Name..vi Exiting the Script with Error !"
    sys.exit(1)
    
print "CHECKING ALL VARIABLES ---------------------------------------------------------------------- \n"
print "test_name : " + test_name


		
def connectalldyn(test_name):
    if test_name == "connectalldyn":   
        print "TESTING FOR : ---------- " + test_name + " ---------- "
        test_to_execute = "python connect_all_dyn.py > /home/CSE_CONSOLE/con_all_script.log "
        print "Executing : " + test_name
        print "Command : " + test_to_execute
        os.system(test_to_execute)
        time.sleep(3)
        checkUUID = "cat /sys/kernel/debug/mei0/meclients > /home/CSE_RESULT/con_all_dyn.log"
        os.system(checkUUID)
        time.sleep(3)
        print "Test is executed successfully ---------------------------------- \n"
    else: 
        print "Test is Fail"

def rearrange1():
    log_data1=open("/home/CSE_CONSOLE/con_all_script.log")
    log_data2=open("/home/CSE_CONSOLE/con_all_script2.log",'w')
    for log_data in log_data1:
        new_log = log_data.split(' ',1)[1]
        log_data2.write(new_log)
	
def rearrange2():	
    log_data2=open("/home/CSE_RESULT/con_all_dyn.log")
    os.system("sed '1d' /home/CSE_RESULT/con_all_dyn.log > /home/CSE_RESULT/new_con_all_dyn.log")
    new_log=open("/home/CSE_RESULT/new_con_all_dyn.log",'rw')
    new_log2=open("/home/CSE_RESULT/new_con_all_dyn2.log",'w')
    for line in new_log.readlines():
        a= line.split("|")
        if (a[4])!='  0':
            ss=a[3]
        else:
            break
        new_log2.write(ss + "\n")


def compare():
    diff= call("diff /home/CSE_CONSOLE/con_all_script2.log /home/CSE_RESULT/new_con_all_dyn2.log", shell=True)
    if diff == 0:
        verdict = "YES"
    else:
        verdict = "NO"
    print "Compare Done !! ----------------------------------------------------------------- \n"
    return verdict

    
def main (test_name):
        os.system("mkdir /home/CSE_RESULT/")
        os.system("mkdir /home/CSE_CONSOLE/")
        os.system("echo 0 >/home/CSE_CONSOLE/con_all_script2.log")
        os.system("echo 0 >/home/CSE_RESULT/new_con_all_dyn2.log")
        connectalldyn(test_name)
        rearrange1()
        rearrange2()
        if test_name == "connectalldyn":
            verdict=compare()
        if verdict == "YES":
            print "\nFINAL VERDICT: Test PASS!!"
            sys.exit(0)
        else:
            print "\nFINAL VERDICT: Test FAIL!!"
            sys.exit(1)
        
        print "Time After execution : " + time.strftime("%H:%M:%S")
        sys.exit(0)   
        
#main
if __name__ == "__main__":
    main (test_name)