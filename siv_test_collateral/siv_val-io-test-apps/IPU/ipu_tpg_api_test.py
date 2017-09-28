#!/usr/bin/python

import sys
import os
import re
import subprocess
import argparse
import os.path
import shutil
import time

#Run command ~ python ipu_lapan.py -t CI_TPG_IPU4_IOCTL_STREAMON_Normal_Check_Noblock_Userptr_Raw8_1920x1080 | tee -a /Complete_result.log
#variables
test_script_name = "/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/pit_tpg_test.sh"
log_dir = "/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/results"
my_log = "/home/siv_test_collateral/siv_val-io-test-apps/IPU/TPG_log_" + time.strftime("%d_%m_%Y")

#parameters
script_name = str(sys.argv[0])
usage="This program gets the output of the cat file and compare it with the input keyword. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-t', help='test_name/run_all')
args = parser.parse_args()

if args.t is not None:
    test_name = args.t
else:
    print "Argument missing for Test Name..Exiting the Script with Error !"
    sys.exit(1)
    
print "CHECKING ALL VARIABLES ---------------------------------------------------------------------- \n"
print "test_script_name : " + test_script_name
print "log_dir : " + log_dir
print "test_name : " + test_name
print "CHECKING ALL VARIABLES ---------------------------------------------------------------------- \n"

def log_fnc(string_to_save,my_log):
    os.system('echo ' + string_to_save + ' >> ' + my_log )
    
def execute(command):
    response = ""
    for element in os.popen(command):
        response += element
    return response
    
def split_fnc(key_string):
    splitter = re.compile("\n")
    read_list = splitter.split(key_string)
    return read_list

def dir_exist(dir_to_check,file_or_dir):
    if file_or_dir == "dir":   
        if os.path.isdir(dir_to_check) == True :
            print "Directory {0} exists \n".format(dir_to_check)
        else:
            print "Directory {0} does not exist..Exiting the Script \n".format(dir_to_check)
            sys.exit(1)
    else:
        if os.path.isfile(dir_to_check) == True :
            print "File {0} exists \n".format(dir_to_check)
        else:
            print "File {0} does not exist..Exiting the Script \n".format(dir_to_check)
            sys.exit(1)

#check the test_script and execute the test        
def Tpg_testcases(test_name,test_script_name,my_log):
    if test_name != "run_all":   
        test_to_execute = "NULL"
        print "Searching for Test case ---------------------------------------- \n"     
        time.sleep(1)
        cat_list = split_fnc(execute('cat ' + test_script_name))
        print "TESTING FOR : ---------- {0} ---------- \n".format(test_name)
        cmd_log = "TESTING FOR : ---------- " + test_name + " ---------- "
        log_fnc(cmd_log,my_log)
        for line in cat_list:
            if re.search(test_name, line):
                test_to_execute = line
        time.sleep(1)
        if test_to_execute == "NULL":
            print " Invalid test_name...Exiting the Script with error "
            sys.exit(1)
        else:        
            print "Executing : " + test_name
            print "Command : " + test_to_execute
            os.system(test_to_execute)
            time.sleep(3)
            print "Test is executed successfully ---------------------------------- \n"
    else:
        print "TESTING FOR : ---------- {0} ---------- \n".format(test_name)
        cmd_log = "TESTING FOR : ---------- " + test_name + " ---------- "
        log_fnc(cmd_log,my_log)
        print "Executing : sh {0}".format(test_script_name)       
        os.system('sh ' + test_script_name)
        time.sleep(6)
        
#check if the created_log exist and search the log for verdict and then return the verdict
def single_check_log(log_dir,test_name,my_log):
    verdict = "PASS"
    created_log = log_dir + "/" + test_name +".log"
    dir_exist(created_log,"file")
    print "Searching the Log File for Test Verdict ---------------------------------------- \n"
    time.sleep(1)
    cat_list = split_fnc(execute('cat ' + created_log))
    print "TESTING FOR : ---------- {0} ---------- \n".format(test_name)
    for line in cat_list:
        if re.search('FAILED', line):
            print "FAILED_HERE : " + line
            verdict = "FAIL"
            cmd_log = "FAILED_HERE : " + line
            log_fnc(cmd_log,my_log)
    print "Test {0} is {1} ! \n".format( test_name, verdict )
    cmd_log = "Test " + test_name + " is " + verdict
    log_fnc(cmd_log,my_log)
    log_fnc(" ",my_log)
    print "Search Done !! ----------------------------------------------------------------- \n"
    return verdict
    
def run_all_check_log(test_script_name,log_dir,my_log):
    cat_list = split_fnc(execute('cat ' + test_script_name))
    print "Searching for log name ---------------------------------------------- /n"   
    for line in cat_list:
        if re.search('CI_TPG_IPU4_IOCTL', line):           
            test_name = line.split(None)[2]
            verdict = single_check_log(log_dir,test_name,my_log)
            if verdict == "PASS":
                print "\nFINAL VERDICT: Test PASS!!"            
            else:
                print "\nFINAL VERDICT: Test FAIL!!"
    print "Search done for all logs -------------------------------------------- /n"
    
def main (test_name,test_script_name,my_log):
    #os.system("cp -r sw_val /home/root/")
    if test_name != "run_all":
        dir_exist(test_script_name,"file")
        Tpg_testcases(test_name,test_script_name,my_log)    
        verdict = single_check_log(log_dir,test_name,my_log)
        print "Time After execution : " + time.strftime("%H:%M:%S")
        if verdict == "PASS":
            print "\nFINAL VERDICT: Test PASS!!"
            sys.exit(0)
        else:
            print "\nFINAL VERDICT: Test FAIL!!"
            sys.exit(1)
    else:
        dir_exist(test_script_name,"file")
        Tpg_testcases(test_name,test_script_name,my_log)
        run_all_check_log(test_script_name,log_dir,my_log)
        print "Time After execution : " + time.strftime("%H:%M:%S")
        sys.exit(0)    
#main
if __name__ == "__main__":
    main (test_name,test_script_name,my_log)