#Created by: Quek, Zhen Han Deric (11576007)
#Description: Part 2 for serial console test
#Dependencies and pre-requisites: N/A
#Last modified by: Quek, Zhen Han Deric (11576007)
#Last modified date: 21 OCT 2016
#Modification description: N/A


import os
import sys
import re
import time
import subprocess

def get_screen_id():
    ID_list = []
    global f_ID_list
    f_ID_list = []
    os.system("screen -ls | grep -i pts > screen_session_id.log")
    with open("screen_session_id.log") as f:
        for line in f:
            ID = re.search(r'\d+\.pts', line)
            if ID:
                ID_list.append(ID.group(0))
    #print ID_list
    
    for line in ID_list:
        f_ID = re.search(r'\d+', line)
        if f_ID:
            f_ID_list.append(f_ID.group(0))
    if len(f_ID_list) == 0:
        f_ID_list.append("1000")
    print f_ID_list
    

def main():
    #print "----- Hi, i m fren Serial Console Test -----"

    time.sleep(3)

    #cmd_start_screen = "screen /dev/ttyUSB0 115200"
    #os.system(cmd_start_screen)

    #subprocess.Popen(["nohup", "python", "serial_console_fren.py"])
    #subprocess.Popen(["screen", "/dev/ttyUSB0 115200"])

    get_screen_id()
    get_log = " | tee -a serial_console_test.log"
    cmd_screen_login1 = "screen -S " + f_ID_list[0] + " -X stuff '^M'" + get_log
    cmd_screen_login2 = "screen -S " + f_ID_list[0] + " -X stuff 'root^M'" + get_log
    cmd_screen_logout = "screen -S " + f_ID_list[0] + " -X stuff 'exit^M'" + get_log
    cmd_screen_kill = "screen -X -S " + f_ID_list[0] + " quit" + get_log
    os.system(cmd_screen_login1)
    time.sleep(3)
    os.system(cmd_screen_login2)
    time.sleep(3)
    os.system(cmd_screen_logout)
    time.sleep(3)
    os.system(cmd_screen_kill)

    #print cmd_screen_login1

main()

