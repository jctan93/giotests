import sys
import os
import re
import time
import argparse
import GenericCommand
import string
import common
from datetime import date, datetime

#sample-command : python gpio_gio.py -i 172.30.248.76 -p 423 -t export -v 0 -d in
#sample-command : python gpio_gio.py -i 172.30.248.76 -p 423 -t change_direction -v 0 -d in
#sample-command : python gpio_gio.py -i 172.30.248.76 -p 423 -t change_value -v 0 -d in
#sample-command : python gpio_gio.py -i 172.30.248.76 -p 423 -t unexport -v 0 -d in

gcs_port = "2300" # GenericCommandServer default port is 2300

# Get Values from Parameter
script_name = str(sys.argv[0])
usage="This program executes gpio cases\n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-i', help='SUT IP')
parser.add_argument('-p', help='Pin_number')
parser.add_argument('-t', help='Test_case [export,change_direction,unexport,read_value]')
parser.add_argument('-v', help='Value')
parser.add_argument('-d', help='Direction')

args = parser.parse_args()

if args.i is not None:
    dut_ip1 = args.i
if args.p is not None:
    pin_number = args.p
if args.t is not None:
    testcase = args.t
if args.v is not None:
    value = args.v
if args.d is not None:
    direction = args.d
    
gpio_dir="/sys/class/gpio"
pin_num="/gpio" + pin_number            #eg : /gpio421
pin_dir= gpio_dir + pin_num             #eg : /sys/class/gpio/gpio421
dir= pin_dir + "/direction"             #eg: /sys/class/gpio/gpio421/direction
val= pin_dir + "/value"                 #eg: /sys/class/gpio/gpio421/value
export_dir = gpio_dir + "/export"       #eg: /sys/class/gpio/gpio421/export 
unexport_dir = gpio_dir + "/unexport"   #eg: /sys/class/gpio/gpio421/unexport 
    
dut = GenericCommand.GenericCommand()
dut.login(dut_ip1,gcs_port)

def split_fnc(cat_out):
    splitter = re.compile("\n")
    read_list = splitter.split(cat_out)
    # print read_list[0]
    return read_list[0]

def export(pin_number,export_dir,pin_dir):
    print "TEST NAME : Export"
    export_cmd = "echo "+ pin_number + " > " + export_dir 
    check = '[ -d "' + pin_dir + '" ] && echo "PASS" || echo "FAIL"'
    dut.execute(export_cmd)
    existance = split_fnc(dut.execute(check))
    return existance

def input_output_pin(pin_number,direction,dir):
    print "TEST NAME : Change_Pin_Direction"
    verdict = "NULL"
    print "Current pin direction : " + split_fnc(dut.execute("cat " + dir))
    print "Changing pin direction......"
    time.sleep(5)
    dut.execute("echo "+ direction + " > " + dir)
    read_cat = split_fnc(dut.execute("cat " + dir))
    print "Pin direction after the change : " + read_cat
    if read_cat == direction:
        verdict = "PASS"
    else:
        verdict = "FAIL"
    return verdict

def read_value(pin_number,value,val):
    print "TEST NAME : Read_Pin_Value"
    verdict = "NULL"
    read_cat = split_fnc(dut.execute("cat " + val))
    print "Pin value : " + read_cat
    if read_cat != '':
        verdict = "PASS"
    else:
        verdict = "FAIL"
    return verdict
    
def unexport(pin_number,unexport_dir,pin_dir):
    print "TEST NAME : Unexport"
    export_cmd = "echo "+ pin_number + " > " + unexport_dir 
    check = '[ -d "' + pin_dir + '" ] && echo "FAIL" || echo "PASS"'
    dut.execute(export_cmd)
    existance = split_fnc(dut.execute(check))
    return existance

def main():
    verdict = "empty"
    if testcase == "export":
        verdict = export(pin_number,export_dir,pin_dir)
    elif testcase == "change_direction":
        verdict = input_output_pin(pin_number,direction,dir)
    elif testcase == "read_value":
        verdict = read_value(pin_number,value,val)
    elif testcase == "unexport":
        verdict = unexport(pin_number,unexport_dir,pin_dir)
    else:
        print "Invalid Test case..SYSTEM EXITING !!"
        sys.exit(1)
    print "Executing : " + testcase
    # print verdict
    if verdict == "PASS":
        print "\nFINAL VERDICT: Test PASS!!"
        sys.exit(0)
    else:
        print "\nFINAL VERDICT: Test FAIL!!"
        sys.exit(1)
              
if __name__ == "__main__":
    main()
    

    
    
