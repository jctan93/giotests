import sys
import os
import re
import time

from datetime import date, datetime

import subprocess
#import GenericCommand
import getopt


    
#
# This function will removed directory passed into it and with successful / unsuccessful return
#
def execute(cmd):

	output = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
	if not output[1]:
		return output[0]
	else:
		return output[1]
	
def rmdir (directory, testVerdict, testlog, OS):
    #print "in rmdir"
    if (OS == "fedora16"):
    	cmd_rmdir = "rmdir " + directory
    elif (OS == "android"):
    	cmd_rmdir = "adb shell rmdir " + directory 
    #print cmd_rmdir	
    if (OS == "fedora16"):
    	cmd_checkdir = "if test -d " + directory + " ; then echo exist; fi"
    if (OS == "android"):
    	cmd_checkdir = "adb shell \"if test -d " + directory + " ; then echo exist; fi\""
    #print cmd_checkdir
    ret = execute(cmd_checkdir)
    print "Check Directory: "
    print "Directory " + directory + " " + ret
    if re.search ("exist", ret):
	print directory + " exist. Removing directory ... "
	cmd_logging = "echo " + directory + " exist. Removing directory ... >> " + testlog
	execute(cmd_logging)
	execute(cmd_rmdir)
    ret = execute(cmd_checkdir)
    if re.search ("exist", ret):
	print directory + " is not removed properly "
	cmd_logging = "echo " + directory + " could not be removed >> " + testlog
	execute(cmd_logging)
#	testVerdict = False
    else:
	print directory + " is removed \n"
	cmd_logging = "echo " + directory + " is removed >> " + testlog
	execute(cmd_logging)

    return testVerdict 



#
# This function will check if a folder is empry. Boolean true will be returned if folder is empty.  
# Boolean False will be returned if folder is not empty.  
#

def check_folder_empty(directory, OS):
    if (OS == "fedora16"):
    	cmd_checkfile = "ls " + directory + " | wc -l"
    elif (OS == "android"):
	cmd_checkfile = "adb shell ls " + directory + " | wc -l"
    ret = execute(cmd_checkfile)
    directory_empty=False
    if re.search ("0", ret):
	directory_empty=True
    else:
	directory_empty=False
    
    return directory_empty

#
# This function will check if file exists. Boolean true will be returned if file exists.  
# Boolean False will be returned if file does not exist.  
#

def check_file_exist(file_location, OS):
    if (OS == "fedora16"):
    	cmd_checkfile = "if test -f " + file_location + " ; then echo exist; fi"
    elif (OS == "android"):
	cmd_checkfile = "adb shell \"if test -f " + file_location + " ; then echo exist; fi\""
    ret = execute(cmd_checkfile)
    file_exist=False
    if re.search ("exist", ret):
	file_exist=True
    else:
	file_exist=False
    
    return file_exist




#
# This function will check if directory exists. Boolean true will be returned if directory exists.  
# Boolean False will be returned if directory does not exist.  
#

def check_dir_exist(dir_location, OS):
    if (OS == "fedora16"):
    	cmd_checkdir = "if test -d " + dir_location + " ; then echo exist; fi"
    elif (OS == "android"):
	cmd_checkdir = "adb shell \"if test -d " + dir_location + " ; then echo exist; fi\""
    ret = execute(cmd_checkdir)
    dir_exist=False
    if re.search ("exist", ret):
	dir_exist=True
    else:
	dir_exist=False
    
    return dir_exist

#
# This function will check if log directory exists. Boolean true will be returned if directory exists.  
# Boolean False will be returned if directory does not exist.  
#

def check_log_dir_exist(dir_location):
    
    cmd_checkdir = "if test -d " + dir_location + " ; then echo exist; fi"
    ret = execute(cmd_checkdir)
    dir_exist=False
    if re.search ("exist", ret):
	dir_exist=True
    else:
	dir_exist=False
    
    return dir_exist


#
# This function will check if directory exists. If it doesn't exist, the directory  
# will be created
#

def create_log_dir(dir_location, OS):
    dir_exist=False
    if (check_log_dir_exist(dir_location) == True):
	print dir_location + " exist. Skip directory creation ... "
        dir_exist=True
    else:
	print dir_location + " does not exist. Creating folder ... "
	if (OS == "fedora16"):
		cmd_mkdir = "mkdir " + dir_location	
	elif (OS == "android"):
		cmd_mkdir = "adb shell mkdir " + dir_location
	execute(cmd_mkdir)

    if dir_exist == False:
    	if (check_log_dir_exist(dir_location) == True):
		print dir_location + " is created "
    	else:
		print dir_location + " is not created "




#
# This function will sum the CPU% and MEM% through top command on the system for data transfer
#

def get_memory_and_cpu_data_transfer(performancelog, OS, destination_file):
     file_non_exist = True
     while(file_non_exist):
        print "waiting for cp to start"
        if (check_file_exist(destination_file, OS) == True):
	    file_non_exist = False
     print "starting cpu monitoring"
     get_cp_memory_cpu = "top -n 10 | grep -w 'cp -f' | grep -v 'grep' | awk '{print $10 \",\" $11}' >> " + performancelog
     
     output = execute(get_cp_memory_cpu)
     print "memory and cpu execute" + output
#     for lines in output:
#	lines = lines.strip()
#	cmd_logging = "echo copy," + lines + " >> " + performancelog
#        run_command(server, userName, passwd, cmd_logging)
#	print lines


#
# This function will sum the CPU% and MEM% through top command on the system 
#

def get_memory_and_cpu(operation, performancelog, OS):
#    time.sleep(10) #wait for copy to happen before getting the memory and cpu usage.
#    print "started get_memory_and_cpu"
    if (OS == "fedora16"):
    	cmd_get_cpu = "ps aux | awk '{ sum += $3}; END { print sum }'"
    	cmd_get_mem = "ps aux | awk '{ sum += $4}; END { print sum }'"
    elif (OS == "android"):
	cmd_get_cpu = "adb shell ps aux | awk '{ sum += $3}; END { print sum }'"
    	cmd_get_mem = "adb shell ps aux | awk '{ sum += $4}; END { print sum }'"
    cpu_result=execute(cmd_get_cpu)
    mem_result=execute(cmd_get_mem)
    cpu_result = cpu_result.rstrip("\n\r")
    mem_result = mem_result.rstrip("\n\r")
    print "%CPU " + cpu_result
    print "%MEM " + mem_result
    cmd_logperf = "echo " + operation + "," + cpu_result + "," + mem_result + " >> " + performancelog
    print cmd_logperf
    execute(cmd_logperf)



#
# This function will unmount all mount point of a particular device. The directory of the moint 
# point will be removed as well
#
def unmount_all (device, testVerdict, testlog, OS):
    if (OS == "fedora16"):
    	cmd_search_mount_point = "df | grep " + device + " | awk '{print $6}'"
    elif (OS == "android"):
	cmd_search_mount_point = "adb shell df | grep " + device + " | awk '{print $6}'"
    #print cmd_search_mount_point	
    ret = execute(cmd_search_mount_point)
    print ret
    mount_points = ret.split("\n")
    for mount in mount_points:
        if(mount != ""):
	    if( OS == "fedora16"):	
	    	cmd_unmount = "umount " + mount + "*"
		print cmd_unmount
	    elif( OS == "android"):
		cmd_unmount = "adb shell umount " + mount + "*"
	        print cmd_unmount
            ret = execute(cmd_unmount)
#	    execute("adb shell rmdir " + mount)
	    rmdir (mount, testVerdict, testlog, OS)

    ret = execute(cmd_search_mount_point)
    if (ret == ""):
	print "All mount points has been unmounted. \n"
	cmd_logging = "echo All mount points has been unmounted >> " + testlog
    else:
	print "Not all mount points has been unmounted. \n"
	cmd_logging = "echo Not all mount points has been unmounted >> " + testlog
	cmd_logging = "echo " + ret + " >> " + testlog
	testVerdict = False
	

    return testVerdict

#
# This function will return today's date
#

def get_date():
    today = date.today()
    day = str(today.day)
    month = str(today.month)
    year = str(today.year)

    if(len(day)==1):
	day = "0" + day 
    if(len(month)==1):
    	month = "0" + month

    currentDate = year +"." + month + "." + day
    return currentDate

#
# This function will return current time for timestamp
#

def get_current_time():
   currentTime = datetime.time(datetime.now()) 
   time_Hour = currentTime.hour
   time_Minute = currentTime.minute
   time_Second = currentTime.second
   Time_now = str(time_Hour) + "." + str(time_Minute) + "." + str(time_Second)
   return Time_now