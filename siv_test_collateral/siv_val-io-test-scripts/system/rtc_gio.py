import sys
import os
import re
import time
import argparse
import GenericCommand
import string
import common
from ssh_util import *
from datetime import date, datetime

#sample command : python rtc_gio.py -i 172.30.248.76 -t Access_time/Read_alarm
#sample command : python rtc_gio.py -i 172.30.248.76 -t Read_alarm

gcs_port = "2300" # GenericCommandServer default port is 2300
Final_Verdict = "NULL"
script_location = "/home/siv_test_collateral/siv_val-io-test-apps/rtc/"
# Get Values from Parameter
script_name = str(sys.argv[0])
usage="This program executes rtc test cases\n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-i', help='SUT IP')
parser.add_argument('-t', help='Test_case [Access_time, Read_alarm]')

args = parser.parse_args()

if args.i is not None:
    dut_ip1 = args.i
if args.t is not None:
   if args.t == "Access_time":
        test_case = "Access_time"
   elif args.t == "Read_alarm":
        test_case = "Read_alarm"
   elif args.t == "check_driver":
        test_case = "Check_driver"
   else:
        print "invalid Test Case name...Exiting the script with ERROR !"
        sys.exit(1)
    
dut = GenericCommand.GenericCommand()
dut.login(dut_ip1,gcs_port)

def reboot_sys(_timeout,dut1):
    print "Rebooting DUT..."
    #dut.timeexecute("reboot")
    #modified by willam
    ssh_agent = ssh_com("172.30.249.86")
    ssh_agent.ssh_exec("python /root/BXT_Daily_Automation/GPIO.py 5")
    ssh_agent.ssh_exec("python /root/BXT_Daily_Automation/GPIO.py 1")
    time.sleep(120)
    dut1_alive = dut.pingalive(dut1,timeout=_timeout)
    if dut1_alive:
        print "[SUT1]Reboot process completed"
    else:
        print "DUT1 is not alive, rebooting process failed"
               
def Access_time_fnc(dut_ip1):
    Verdict_date="PASS"
    Verdict_minute="PASS"
    Verdict_hour="PASS"
    print "Running Access Time"
    Minute_pass="FAIL"
    date_time_before_change = dut.execute("date")
    date_time_before_reboot = dut.execute("date -s '2015-12-3 11:12:13'")
    date_time_after_change = dut.execute("date")
    date_before_reboot = dut.execute("date +'%D'")
    hour_before_reboot = dut.execute("date +'%H'")
    minute_before_reboot = dut.execute("date +'%M'")
    
    print "date_time_before_change : " + date_time_before_change
    print "date_time_after_change : " + date_time_after_change
    print "date_time_before_reboot : " + date_time_before_reboot
    print "date_before_reboot : " + date_before_reboot 
    print "hour_before_reboot : " + hour_before_reboot
    print "minute_before_reboot : " + minute_before_reboot
    
    reboot_sys(150,dut_ip1)
     
    date_time_after_reboot=dut.execute("date")
    date_after_reboot=dut.execute("date +'%D'")
    hour_after_reboot=dut.execute("date +'%H'")
    minute_after_reboot=dut.execute("date +'%M'")
    
    print "Date_time before reboot is : " + date_time_before_reboot
    print "Date_time after reboot is : " + date_time_after_reboot
    
    print "date_before_reboot : " + date_before_reboot 
    print "date_after_reboot : " + date_after_reboot 
    
    if ( str(date_before_reboot) == str(date_after_reboot) ):
        print("Date before reboot and After reboot are the same")
    else:
        print("ERROR: Date before reboot and After reboot are the different..Test FAIL")
        print "date_before_reboot : " + date_before_reboot 
        print "date_after_reboot : " + date_after_reboot 
        Verdict_date="FAIL" 

    if ( str(hour_before_reboot) == str(hour_after_reboot) ):
        print("Hour before reboot and After reboot are the same")
        for num in range (0,10):
            edit_minute=int(minute_after_reboot) + num
            if ( edit_minute == int(minute_after_reboot)):
                Minute_pass="PASS"
 
        print "MInute_pass : " + Minute_pass
        if (Minute_pass == "PASS"):
            print("Minute before reboot and After reboot are within 10 minute range")
        else:
            print("ERROR: Minute before reboot and After are not within 10 minute range..Test FAIL")
            print "minute_before_reboot : " + minute_before_reboot
            print "minute_after_reboot : " + minute_after_reboot
            Verdict_minute="FAIL"
    else:
        print("ERROR: Hour before reboot and After reboot are the different..Test FAIL")
        print "hour_before_reboot : " + hour_before_reboot
        print "hour_after_reboot : " + hour_after_reboot
        Verdict_hour="FAIL"
                  
    if Verdict_date == "FAIL" or Verdict_minute == "FAIL" or Verdict_hour == "FAIL":
        return "FAIL"
    else:
        return "PASS"
        
def Read_alarm_fnc():
	print "Triggering rtctest app"
	if dut.execute(script_location + "rtctest") == "":
		print "Wake On RTC Test: PASS"
		return "PASS"
	else:
		print "Wake On RTC Test: Fail"
		return "FAIL"

def Check_driver():
	if dut.execute("ls -l /dev/ | grep -i rtc") != "" and dut.execute("dmesg | grep -i rtc") != "":
		return "PASS"
	else:
		return "FAIL"


if __name__ == "__main__":
	print test_case
	if test_case == "Access_time":
		Final_Verdict = Access_time_fnc()
	elif test_case == "Read_alarm":
		Final_Verdict = Read_alarm_fnc()
	elif test_case == "Check_driver":
		Final_Verdict = Check_driver()
		
	if Final_Verdict == "PASS":
		print "\nFINAL VERDICT: Test PASS!!"
		sys.exit(0)
	else:
		print "\nFINAL VERDICT: Test FAIL!!"
		sys.exit(1)
	 


               
