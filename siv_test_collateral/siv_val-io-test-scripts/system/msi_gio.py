import sys
import os
import re
import time
import argparse
import GenericCommand
import string
import common
from datetime import date, datetime

#sample command to run python msi_gio.py -i 172.30.248.76 

script_name = str(sys.argv[0])
dev_1_ip = "172.30.249.63"
gcs_port = "2300" # GenericCommandServer default port is 2300
file_path = "/proc/interrupts"
search_keyword = "PCI-MSI"

usage= " This program Execute Msi test case ! "

parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-i', help='SUT IP')

args = parser.parse_args()

if args.i is not None:
    dev_1_ip = args.i
    	
dut = GenericCommand.GenericCommand()
dut.login(dev_1_ip,gcs_port)

#-----Program Starts Here----------------
def check_file_exist():
    print " "
    print "SEARCHING FOR Proc Interupt FILE------------"
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
    print "SEARCH ENDS---------------------------------"
    
def test_execute():
    verdict = "FAIL"
    cat_out = dut.execute("cat " + file_path)
    print "----------------------------------------------------------------------------"
    print "SEARCH_KEYWORD : " + search_keyword 
    print "SEARCH_USING : cat " + file_path
    print "----------------------------------------------------------------------------"
    time.sleep(2)

    splitter = re.compile("\n")
    read_list = splitter.split(cat_out)
    
    for line in read_list:
        if re.search(str(search_keyword) ,line):
            print "Keyword Found : " + line
            verdict = "PASS"
    print ""
    print "TEST VERDICT: " + verdict
    
    return verdict

def main():
    check_file_exist()
    verdict = test_execute()
    if verdict == "PASS":
        print "\nFINAL VERDICT: Test PASS!!"
        sys.exit(0)
    else:
        print "\nFINAL VERDICT: Test FAIL!!"
        sys.exit(1)
     
if __name__ == "__main__":
    main()
