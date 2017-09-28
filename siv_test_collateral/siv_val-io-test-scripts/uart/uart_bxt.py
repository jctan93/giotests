# This script was written specifically for AlpineValley validation. It is for both UART & HSUART
# Currently supports loopback UART tests
# Author: Henri 11472439
# Created: 9 April 2013
# Modified: 
# 23 April 2015, Henri - Tweaked buffer time. Added retry loop and debug message. Disabled logging due to bug not fixed.
# Status: Deployed; Logging still has error
# Modified: 
# 1 December 2015, Kahu - Modified the script to test using single Uart_port only (uart_port_1 = "/dev/ttyS1").Modified default variable to a FAIL test case. 
# Status: Deployed; Logging to (/UART_LOG2 ) in SUT

import sys
import os
import re
import time
import argparse
import GenericCommand
import string
import common
import subprocess
from datetime import date, datetime

script_name = str(sys.argv[0])

# Device settings
uart_port_1 = "/dev/ttyS1" # Check in /dev for ttySx or ttyPCHx

log_file = "/LOG/uart/uart_"+ common.get_date()
gcs_port = "2300" # GenericCommandServer default port is 2300


# Default Variables
baud_rate = 5000000
data_bit = 9
parity = "I"
stop_bits = 3
flow_control = "I"
#iterations = 1
test_app_location = "/home/siv_test_collateral/siv_val-io-test-apps/uart/"
test_script_location = "/home/siv_test_collateral/siv_val-io-test-scripts/uart/"
test_app = "ioh_uart"
uart_port_1 = "/dev/ttyS1"

 
# Get Values from Parameter
usage="This program executes ioh_uart rx-tx automatically with the parameters given.\n"

parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-i', help='SUT IP')
parser.add_argument('-thm_ip', help='THM IP')
parser.add_argument('-m', help='mode. Example: txr[default], rxr, txaa')
parser.add_argument('-b', help='Baud rate')
parser.add_argument('-d', help='Data bits [5, 6, 7, 8]')
parser.add_argument('-p', help='Parity [none, odd, even, mark, space]')
parser.add_argument('-s', help='Stop Bits [1, 1.5, 2]')
parser.add_argument('-f', help='Flow Control [none, hardware, software]')
parser.add_argument('-it', help='Iterations')
parser.add_argument('-tc', help='Test Case')
parser.add_argument('-pci', help='ACPI,PCI')

args = parser.parse_args()

if args.i is not None:
    dev_1_ip = args.i
if args.thm_ip is not None:
    dev_2_ip = args.thm_ip
if args.m is not None:
    if str(args.m) == "txr" or str(args.m).upper() == "TXR":
        mode = "txr" 
    elif str(args.m) == "rxr" or str(args.m).upper() == "RXR":
        mode = "rxr" 
    elif str(args.m) == "txaa" or str(args.m).upper() == "TXAA":
        mode = "txaa" 
if args.f is not None:
   if str(args.f).upper() == "NONE" or str(args.f).upper() == "N":
      flow_control = "N"
   elif str(args.f).upper() == "HARDWARE" or str(args.f).upper() == "H":
      flow_control = "H"
   elif str(args.f).upper() == "SOFTWARE" or str(args.f).upper() == "S":  
      flow_control = "S"
if args.d is not None:
    data_bit = args.d
if args.p is not None:
   if str(args.p).upper() == "NONE" or str(args.p).upper() == "N":
      parity = "N"
   elif str(args.p).upper() == "ODD" or str(args.p).upper() == "O":
      parity = "O"
   elif str(args.p).upper() == "EVEN" or str(args.p).upper() == "E":
      parity = "E"
   elif str(args.p).upper() == "MARK" or str(args.p).upper() == "M":
      parity = "M"
   elif str(args.p).upper() == "SPACE" or str(args.p).upper() == "S":
      parity = "S"
if args.s is not None:
   if args.s == "1.5":
     stop_bits = "15"
   else:
     stop_bits = str(args.s)
if args.b is not None:
    baud_rate = args.b
if args.pci is not None:
    pci = args.pci
if args.it is not None:
    iterations = args.it
    
if args.tc is None:
    tc = ""
elif args.tc is not None:
    tc = args.tc

dut = GenericCommand.GenericCommand()
dut.login(dev_1_ip,gcs_port)
thm = GenericCommand.GenericCommand()
thm.login(dev_2_ip,gcs_port)

#print iterations
# DEFINITION

def loopback_tx_rx():
    os.environ["TERM"] = "xterm"
    # Check if not more tx rx activity running form last run in automation environment
    dut.timeexecute("pkill -x ioh_uart")
    thm.timeexecute("pkill -x ioh_uart")

    # Remove old UART log files from previous run
    dut.timeexecute("rm -f /UART_LOG2; rm -f /UART_LOG")

    # Execute TX line after RX with buffer
    if mode == "rxr":
        if tc == "mc":
        # mc = multi-core/threaad-safe
            status = os.system("python " + test_script_location + "serial_console.py " + dev_1_ip)
        dut.timeexecute(test_app_location + test_app + " " + uart_port_1 + " -"+ str(mode) + " " + str(baud_rate) + " " + str(data_bit) + " " + parity + " " + str(stop_bits) + " " + flow_control + " " + str(iterations) + " n s n >> /UART_LOG" )
        time.sleep(5)
        dut.timeexecute(test_app_location + test_app + " " + uart_port_1 + " -txr " + str(baud_rate) + " " + str(data_bit) + " " + parity + " " + str(stop_bits) + " " + flow_control + " " + str(iterations) + " n s n >> /UART_LOG" )
    else:
        dut.timeexecute(test_app_location + test_app + " " + uart_port_1 + " -"+ str(mode) + " " + str(baud_rate) + " " + str(data_bit) + " " + parity + " " + str(stop_bits) + " " + flow_control + " " + str(iterations) + " n s n >> /UART_LOG2" )
    print test_app_location + test_app + " " + uart_port_1 + " -"+ str(mode) + " " + str(baud_rate) + " " + str(data_bit) + " " + parity + " " + str(stop_bits) + " " + flow_control + " " + str(iterations) + " n s n >> /UART_LOG2"

    # THIS LINE WAITS FOR BOTH UART TX RX TO COMPLETE BEFORE READING OUTPUT FROM APP
    # Cleanup & verdict
    if int(baud_rate) <= 50:
        time.sleep(300) # Default = 300
    elif int(baud_rate) > 50 and int(baud_rate) <= 300:
        time.sleep(100) # Default = 60
    elif int(baud_rate) > 300 and int(baud_rate) <= 9600:
        time.sleep(80)  # Default = 40
    elif int(baud_rate) > 9600 and int(baud_rate) <= 115200:
        time.sleep(70)  # Default = 30
    else:
        time.sleep(40)  # Default = 20l

    if mode =="rxr":
        result_2 = dut.execute("cat /UART_LOG")
    else:
        result_2 = dut.execute("cat /UART_LOG2")
    
    if result_2 == "":
        print "\nDEBUG: Output is NULL! Buffer timeout"
    else:
        print "DEBUG: \n" + result_2 # debug use

    time.sleep(3)
    if mode == "rxr":
        if re.search('SUCCESS: 1000 bytes of data written successfully', str(dut.execute("cat /UART_LOG"))) or re.search('Invalid Baud Rate', str(dut.execute("cat /UART_LOG"))) or re.search('Invalid Parity', str(dut.execute("cat /UART_LOG"))) or re.search('Invalid Data bit', str(dut.execute("cat /UART_LOG"))) :
            if tc == "mfc" and re.search("PASS", uart_manual_flow_control()):
                print "UART Manual Flow Control Test: Pass"
            elif tc == "mc" and status == 0:
                print "Serial Console Test: Pass"
            elif tc == "":
                exit
            else:
                print "UART Manual Flow Control Test: Fail"
            print "VERDICT: PASS"
            return True
        else:
            print "VERDICT: FAIL"
            return False
    elif mode == "txr" or mode == "txaa":
        if re.search('SUCCESS: Data sent and received are same', str(dut.execute("cat /UART_LOG2"))):
            print "VERDICT: PASS"
            return True
        else:
            print "VERDICT: FAIL"
            return False

def uart_manual_flow_control():
    dut.execute("rm -rf /UART_FLOWCNTL_LOG")
    dut.execute(test_app_location + "uart_flowcntl >> /UART_FLOWCNTL_LOG")
    return dut.execute("cat /UART_FLOWCNTL_LOG")


def uart_line_break():
    dut.execute("rm -rf /UART_LINE_BREAK_LOG")
    dut.execute(test_app_location + "siginit & >> /UART_LINE_BREAK_LOG")
    #time.sleep(5)
    dut.execute(test_app_location + "uart_line_break")
    print_log = dut.execute("cat /UART_LINE_BREAK_LOG")
    print print_log


# MAIN  
def main():
    if not loopback_tx_rx():
        count = 1 
        while count <= 3:
            print "\nRetry: " + str(count) + "\n===================" 
            if loopback_tx_rx():
                print "\nFINAL VERDICT: UART Test PASS!!"
                sys.exit(0)
            count = count + 1 

        print "\nFINAL VERDICT: UART Test FAIL!!"
        sys.exit(1)
    else:
        print "\nFINAL VERDICT: UART Test PASS!!"
        sys.exit(0)
    """else:
        if tc == "mfc":
            #mfc = uart manual flow control
            uart_manual_flow_control()
        elif tc == "lb":
            #uart line break
            uart_line_break()"""

if __name__ == "__main__":
    main()
