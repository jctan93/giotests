#!/usr/bin/python

import sys
import os
import os.path
import time
import subprocess

os.chdir("/usr/sbin/")
print "Start up resourcemgr ==================================== \n"
print os.path.isfile("resourcemgr")
if os.path.isfile("resourcemgr"):
    proc = subprocess.Popen(['./resourcemgr'], shell=True)
    time.sleep(2)
    resourcemgr_id=proc.pid
    print "resourcemgr_id:" + str(resourcemgr_id) + "\n"
    os.system("kill -9 " + str(resourcemgr_id))
    if resourcemgr_id is not None: 
        print "resourcemgr start up PASS. \n"
        sys.exit(0)
    else:
        print "resourcemgr start up FAIL. \n"
else: 
    print "No such file. Unable to start up resourcemgr. \n"
    print "resourcemgr start up FAIL. \n"
    sys.exit(1)
    
print "Resourmgr test done! ================================ \n" 