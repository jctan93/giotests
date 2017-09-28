import sys
import os
import re
import time
import argparse
import GenericCommand
import string
import common
from datetime import date, datetime

#sample command to run python Thermal_gio.py -ip 172.30.249.27 -p /sys/class/hwmon/hwmon0/temp2_input -it 3

#defaut values
script_name = str(sys.argv[0])
dev_1_ip = "172.30.248.138"
gcs_port = "2300" # GenericCommandServer default port is 2300
file_path = "/sys/class/hwmon/hwmon0/temp1_input"
iteration = 1

#parameters
usage="This program gets the output of the cat file and compare it with the input keyword. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-ip', help='SUT IP')
parser.add_argument('-it', help='iteration')
parser.add_argument('-p', help='file_path')
args = parser.parse_args()

if args.ip is not None:
    dev_1_ip = args.ip
if args.it is not None:
    iteration = args.it
if args.p is not None:
	file_path = args.p

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
    print "SEARCHING FOR THERMAL FILE------------"
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
        print "\nTEST VERDICT: Thermal Test PASS!!"
        verdict = "PASS"
    else:
        print "ERROR: The result of cat {0} is NOT a number ".format(file_path)
        print "The output is {0} ".format(cat_list[0])
        print "\nTEST VERDICT: Thermal Test FAIL!!"
        verdict = "FAIL"
    print "Test End ! -------------------------------------------"
    return verdict
 
def thermal_test():
    check_file_exist(file_path)
    test_verdict = cat_check(file_path)
    return test_verdict
    

#-----Program Starts Here----------------
if __name__ == "__main__":
    if iteration == 1:
        print "-----Running Iteration 1------------------------------"
        final_verdict = thermal_test()
    else:
        for i in range(1,int(iteration)+1):
            print "-----Running Iteration {0}------------------------------".format(i)
            final_verdict = thermal_test()
            print " "
    if final_verdict == "PASS":
        print "\nFINAL VERDICT: Thermal Test PASS!!"
        sys.exit(0)
    else:
        print "\nFINAL VERDICT: Thermal Test FAIL!!"
        sys.exit(1)
        
        
            