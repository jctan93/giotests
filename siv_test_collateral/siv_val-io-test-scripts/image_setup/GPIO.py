import os
import time
import sys

pin_number = sys.argv[1]
timer = sys.argv[2]

if not os.path.exists("/sys/class/gpio/gpio"+ pin_number):
    os.system("echo " + pin_number + " > /sys/class/gpio/export")
os.system("echo out > /sys/class/gpio/gpio"+ pin_number +"/direction")
print "Turn on"
os.system("echo 1 > /sys/class/gpio/gpio"+ pin_number +"/value")
time.sleep(int(timer))
print "Turn off"
os.system("echo 0 > /sys/class/gpio/gpio"+ pin_number +"/value")
