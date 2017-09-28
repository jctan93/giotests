import sys
import os
import re
import time
import argparse
import GenericCommand
import string
import common
from datetime import date, datetime

#sample command to run python pstate_gio.py -ip 172.30.248.76 -i 3 -t min_freq
#sample command to run python pstate_gio.py -ip 172.30.248.76 -i 3 -t max_freq

#defaut values
script_name = str(sys.argv[0])
dev_1_ip = "172.30.248.76"
gcs_port = "2300" # GenericCommandServer default port is 2300
scaling_min_freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq"
scaling_max_freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq"
iteration = 1

#parameters
usage="This program gets the output of the cat file and compare it with the input keyword. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-ip', help='SUT IP')
parser.add_argument('-i', help='iteration')
parser.add_argument('-t', help='test_name[min_freq,max_freq]')
args = parser.parse_args()

if args.ip is not None:
    dev_1_ip = args.ip
if args.i is not None:
    iteration = args.i
if args.t is not None:
    test_name = args.t

dut = GenericCommand.GenericCommand()
dut.login(dev_1_ip,gcs_port)

#This function reads the content of the input variable and store it in list form
def split_fnc(key_string):
    splitter = re.compile("\n")
    read_list = splitter.split(key_string)
    return read_list
            
#This function checks for the existance of the cat file
def check_file_exist(file_path):
    print " "
    print "SEARCHING FOR Pstate FILE------------"
    print " "
    existance = dut.execute("[ -f " + file_path + "  ] && echo 'Found' || echo 'Not found'" )
    print existance
    if re.search("Found" , str(existance)):
        print "File: {0} exists".format(file_path)
    else:
        print "ERROR: File {0} does not exists".format(file_path)
        print " Terminating the Script due to ERROR !"
        sys.exit(1)
    print " "
    print "SEARCH ENDS---------------------------"
    
#This function reads the cat file and check if it's content matches the keyword for cat_type == string
#If cat_type == number, the function will check if the search_keyword is a number and prints the search_keyword
def cat_check(file_path):
    verdict = "NULL"
    print " "
    print "CAT FILE CHECK------------------------"
    print " "
    cat_out = dut.execute("cat " + file_path)
    cat_list = split_fnc(cat_out)
    if str(cat_list[0]).isdigit()== True:
        print "The Content of cat {0} is a number ".format(file_path)
        print "The output is {0} ".format(cat_list[0])
        print "\nTEST VERDICT: Pstate Test PASS!!"
        verdict = "PASS"
    else:
        print "ERROR: The result of cat {0} is NOT a number ".format(file_path)
        print "The output is {0} ".format(cat_list[0])
        print "\nTEST VERDICT: Pstate Test FAIL!!"
        verdict = "FAIL"
    print "Test End ! -------------------------------------------"
    return verdict
 
def Pstate_test():
    if test_name == "min_freq":
        file_path = scaling_min_freq_path
    elif test_name == "max_freq":
        file_path = scaling_max_freq_path
    else:
        print "Invalid test_name..Exiting the script with error !"
        sys.exit(1)
    print "Executing test : " + test_name
    print "File path : " + file_path
    check_file_exist(file_path)
    test_verdict = cat_check(file_path)
    return test_verdict

#-----Program Starts Here----------------
if __name__ == "__main__":
    if iteration == 1:
        print "-----Running Iteration 1------------------------------"
        final_verdict = Pstate_test()
    else:
        for i in range(1,int(iteration)+1):
            print "-----Running Iteration {0}------------------------------".format(i)
            final_verdict = Pstate_test()
            print " "
    if final_verdict == "PASS":
        print "\nFINAL VERDICT: Pstate Test PASS!!"
        sys.exit(0)
    else:
        print "\nFINAL VERDICT: Pstate Test FAIL!!"
        sys.exit(1)
        
        
            