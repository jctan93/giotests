#Created by: Quek, Zhen Han Deric (11576007)
#Description: For serial console test. This is part 1, part 2 (serial_console_fren.py) is required.
#Dependencies and pre-requisites: N/A
#Last modified by: Quek, Zhen Han Deric (11576007)
#Last modified date: 21 OCT 2016
#Modification description: N/A


import os
import sys
import re
import time
import subprocess
import GenericCommand

dut = GenericCommand.GenericCommand()
dut.login(sys.argv[1])

def main():
    print "----- Serial Console Test -----"

    if (os.path.isfile("serial_console_test.log")==1):
        os.system("rm -rf serial_console_test.log")

    time.sleep(2)
    #dut.execute("export TERM=xterm")
    os.environ["TERM"] = "xterm"
    """if not dut.execute("ls -l /home | grep -i serial_console_fren.py"):
        os.system("scp -r /home/automation_config/serial_console_fren.py root@" + sys.argv[1] + ":/home")"""
    subprocess.Popen(["python", "/home/siv_test_collateral/siv_val-io-test-scripts/uart/serial_console_fren.py"])

    cmd_start_screen = "screen /dev/ttyUSB0 115200"
    os.system(cmd_start_screen)

    #sub = subprocess.Popen("screen /dev/ttyUSB0 115200", shell=True)

    #subprocess.Popen(["nohup", "python", "serial_console_fren.py"])
    #subprocess.Popen(["screen", "/dev/ttyUSB0 115200"])

    #print cmd_screen_login1

    #time.sleep(25)
    #print sub.returncode

    os.system("clear")

    if (os.path.isfile("/home/siv_test_collateral/siv_val-io-test-scripts/uart/serial_console_test.log") == 1 and os.stat("/home/siv_test_collateral/siv_val-io-test-scripts/uart/serial_console_test.log").st_size == 0):
        print "Serial console test : PASS"
        sys.exit(0)
    else:
        print "Serial console test: FAIL"
        sys.exit(1)

main()
