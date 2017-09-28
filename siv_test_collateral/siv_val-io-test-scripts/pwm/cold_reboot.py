import os, sys, time, GenericCommand
from ssh_util import *

minno = GenericCommand.GenericCommand()
minno.login("172.30.248.12", "2300")
os.system("reset")
for i in range (1, int(sys.argv[2])+1):
    print "Start Cold Reboot - Round " + str(i)
    minno.execute("python /root/BXT_Daily_Automation/GPIO.py 83 1")
    time.sleep(5)
    if minno.pingdead(sys.argv[1]):
        if minno.pingalive(sys.argv[1], "2300", 180):
            print "Success Round " + str(i) + "\n"
            verdict = True
        else:
            print "Fail Round " + str(i) + "\n"
            verdict = False
            exit(1)
    else:
        print "SUT not in dead mode"
        exit(1)

if verdict == True:
    print "Test Pass"
    sys.exit(0)
else:
    print "Test Fail"
    sys.exit(1)

minno.execute("python /root/BXT_Daily_Automation/GPIO.py 82 5")
minno.execute("python /root/BXT_Daily_Automation/GPIO.py 82 1")