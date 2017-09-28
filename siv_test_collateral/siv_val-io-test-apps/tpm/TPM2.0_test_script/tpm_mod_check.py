#!/usr/bin/python

import sys
import os
import re
import subprocess
import argparse
import os.path
import shutil
import time

#Run command ~ python tpm_mod_test.py -t tpm_modules_check | tee -a /Complete_result.log
#Run command ~ python tpm_mod_test.py -t tpm0_check | tee -a /Complete_result.log

#variables
log_dir = "/home/root/tpm2.0_test_" + time.strftime("%d_%m_%Y") + "/"
my_log = "/home/root/TPM_log_" + time.strftime("%d_%m_%Y")

#parameters
script_name = str(sys.argv[0])
usage="This program gets the output of the cat file and compare it with the input keyword. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-t', help='test_name < modules_checking | tpm0_check > ')
args = parser.parse_args()

if args.t is not None:
    test_name = args.t
else:
    print "Argument missing for Test Name..Exiting the Script with Error !"
    sys.exit(1)
    
print "CHECKING ALL VARIABLES ---------------------------------------------------------------------- \n"
print "test_name : " + test_name
print "CHECKING ALL VARIABLES ---------------------------------------------------------------------- \n"

def log_fnc(string_to_save, my_log):
    os.system('echo ' + string_to_save + ' >> ' + my_log )

def tpm_testcases(test_name):
    if test_name == "tpm_modules_check":   
        print "TESTING FOR : ---------- {0} ---------- \n".format(test_name)
        cmd_log = "TESTING FOR : ---------- " + test_name + " ---------- "
        log_fnc(cmd_log, my_log)
        test_to_execute = "lsmod > " + log_dir + "tpm_modules_check.log"
        print "Executing : " + test_name
        print "Command : " + test_to_execute
        os.system(test_to_execute)
        time.sleep(3)
        print "Test is executed successfully ---------------------------------- \n"
            
    if test_name == "tpm0_check":
        print "TESTING FOR : ---------- {0} ---------- \n".format(test_name)
        cmd_log = "TESTING FOR : ---------- " + test_name + " ---------- "
        log_fnc(cmd_log, my_log)
        test_to_execute = "ls -l /dev/tpm0 > " + log_dir + "tpm0_check.log "
        print "Executing : " + test_name
        print "Command : " + test_to_execute
        os.system(test_to_execute)
        time.sleep(3)

def tpm_modules_log_check(log_dir,test_name, my_log):
    
    verdict= "FAIL"
    match_tpm = "no_tpm"
    match_tpmcrb = "no_tpmcrb"
    match_tpmtis = "no_tpmtis"
    no_module=list()
    
    module_log=open(log_dir+test_name+".log")
    
    for line in module_log:
        if re.search('tpm', line):
            match_tpm = "is_tpm"
            cmd_log = "Matching Case: " + line
            log_fnc(cmd_log, my_log)
        if re.search('tpm_crb', line):
            match_tpmcrb = "is_tpmcrb"
            cmd_log = "Matching Case: " + line
            log_fnc(cmd_log, my_log)        
        if re.search('tpm_tis', line):
            match_tpmtis = "is_tpmtis"
            cmd_log = "Matching Case: " + line
            log_fnc(cmd_log, my_log)

    if (match_tpm == "is_tpm") and (match_tpmcrb == "is_tpmcrb") and (match_tpmtis == "is_tpmtis"):
        verdict= "PASS"
    else:
        if match_tpm != "is_tpm":
            no_module.append("tpm")
        if match_tpmcrb !=  "is_tpmcrb":
            no_module.append("tpm_crb")
        if match_tpmtis != "is_tpmtis":
            no_module.append("tpm_tis")

        for module in no_module:
            print "Missing Module: " + module
            cmd_log = "Missing Module: " + module
            log_fnc(cmd_log, my_log)
            
    print "Test {0} is {1} ! \n".format( test_name, verdict )
    cmd_log = "Test " + test_name + " is " + verdict
    log_fnc(cmd_log,my_log)
    log_fnc(" ",my_log)
    print "Search Done !! ----------------------------------------------------------------- \n"
    return verdict

def tpm0_log_check(log_dir,test_name, my_log):
    
    verdict= "FAIL"
    
    tpm0_log=open(log_dir+test_name+".log")

    for line in tpm0_log:
        if re.search('tpm0', line):
            verdict= "PASS"
            cmd_log = "Matching Case: " + line
            log_fnc(cmd_log,my_log)

    print "Test {0} is {1} ! \n".format( test_name, verdict )
    cmd_log = "Test " + test_name + " is " + verdict
    log_fnc(cmd_log,my_log)
    log_fnc(" ",my_log)
    print "Search Done !! ----------------------------------------------------------------- \n"
    return verdict
    

def main (test_name):
    os.system("mkdir " + log_dir)
    tpm_testcases(test_name)
    if test_name == "tpm_modules_check":
        verdict=tpm_modules_log_check(log_dir,test_name,my_log)
    if test_name == "tpm0_check":
        verdict=tpm0_log_check(log_dir,test_name,my_log)
        
    if verdict == "PASS":
        print "\nFINAL VERDICT: Test PASS!!"
        sys.exit(0)
    else:
        print "\nFINAL VERDICT: Test FAIL!!"
        sys.exit(1)
        
    print "Time After execution : " + time.strftime("%H:%M:%S")
        
#main
if __name__ == "__main__":
    main (test_name)
