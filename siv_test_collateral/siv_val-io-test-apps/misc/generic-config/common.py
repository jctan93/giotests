import sys
import os
import re
import time
from datetime import date, datetime
import GenericCommand
import getopt
import random
import string
from bitstring import *
  
#
# This function will removed directory passed into it and with successful / unsuccessful return
#

def rmdir (directory, testVerdict, dut, testlog, OS):
    print "in rmdir"
    if (OS == "fedora16"):
        cmd_rmdir = "rmdir " + directory
    elif (OS == "android"):
        cmd_rmdir = "adb shell rmdir " + directory 
    print cmd_rmdir

    if (OS == "fedora16"):
        cmd_checkdir = "if test -d " + directory + " ; then echo exist; fi"
    elif (OS == "android"):
        cmd_checkdir = "adb shell \"if test -d " + directory + " ; then echo exist; fi\""
    print cmd_checkdir

    ret = dut.execute(cmd_checkdir)
    print ret

    if re.search ("exist", ret):
        print directory + " exist. Removing directory ... "
        cmd_logging = "echo " + directory + " exist. Removing directory ... >> " + testlog
        dut.execute(cmd_logging)
        dut.execute(cmd_rmdir)

    ret = dut.execute(cmd_checkdir)

    if re.search ("exist", ret):
        print directory + " is not removed properly "
        cmd_logging = "echo " + directory + " could not be removed >> " + testlog
        dut.execute(cmd_logging)

    else:
        print directory + " is removed"
        cmd_logging = "echo " + directory + " is removed >> " + testlog
        dut.execute(cmd_logging)

    return testVerdict 



#
# This function will check if a folder is empry. Boolean true will be returned if folder is empty.  
# Boolean False will be returned if folder is not empty.  
#

def check_folder_empty(directory, dut, OS):
    if (OS == "fedora16"):
        cmd_checkfile = "ls " + directory + " | wc -l"
    elif (OS == "android"):
        cmd_checkfile = "adb shell ls " + directory + " | wc -l"

    ret = dut.execute(cmd_checkfile)
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

def check_file_exist(file_location, dut, OS):
    if (OS == "fedora16"):
        cmd_checkfile = "if test -f " + file_location + " ; then echo exist; fi"
    elif (OS == "android"):
        cmd_checkfile = "adb shell \"if test -f " + file_location + " ; then echo exist; fi\""

    ret = dut.execute(cmd_checkfile)
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

def check_dir_exist(dir_location, dut, OS):
    if (OS == "fedora16"):
        cmd_checkdir = "if test -d " + dir_location + " ; then echo exist; fi"
    elif (OS == "android"):
        cmd_checkdir = "adb shell \"if test -d " + dir_location + " ; then echo exist; fi\""

    ret = dut.execute(cmd_checkdir)
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

def check_log_dir_exist(dir_location, dut):
    
    cmd_checkdir = "if test -d " + dir_location + " ; then echo exist; fi"
    ret = dut.execute(cmd_checkdir)
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

def create_log_dir(dir_location, dut, OS):
    dir_exist=False

    if (check_log_dir_exist(dir_location, dut) == True):
        print dir_location + " exist. Skip directory creation ... "
        dir_exist=True
    else:
        print dir_location + " does not exist. Creating folder ... "

        if (OS == "fedora16"):
            cmd_mkdir = "mkdir " + dir_location	
        elif (OS == "android"):
            cmd_mkdir = "adb shell mkdir " + dir_location
        dut.execute(cmd_mkdir)

    if dir_exist == False:
        if (check_log_dir_exist(dir_location, dut) == True):
            print dir_location + " is created "
        else:
            print dir_location + " is not created "




#
# This function will sum the CPU% and MEM% through top command on the system for data transfer
#

def get_memory_and_cpu_data_transfer(dut,performancelog, OS, destination_file):
    file_non_exist = True

    while(file_non_exist):
        print "waiting for cp to start"

        if (check_file_exist(destination_file, dut, OS) == True):
            file_non_exist = False

    print "starting cpu monitoring"
    get_cp_memory_cpu = "top -n 10 | grep -w 'cp -f' | grep -v 'grep' | awk '{print $10 \",\" $11}' >> " + performancelog

    output = dut.execute(get_cp_memory_cpu)
    print "memory and cpu execute" + output



#
# This function will sum the CPU% and MEM% through top command on the system 
#

def get_memory_and_cpu(operation, dut,performancelog, OS):

    if (OS == "fedora16"):
        cmd_get_cpu = "ps aux | awk '{ sum += $3}; END { print sum }'"
        cmd_get_mem = "ps aux | awk '{ sum += $4}; END { print sum }'"
    elif (OS == "android"):
        cmd_get_cpu = "adb shell ps aux | awk '{ sum += $3}; END { print sum }'"
        cmd_get_mem = "adb shell ps aux | awk '{ sum += $4}; END { print sum }'"

    cpu_result=dut.execute(cmd_get_cpu)
    mem_result=dut.execute(cmd_get_mem)

    cpu_result = cpu_result.rstrip("\n\r")
    mem_result = mem_result.rstrip("\n\r")

    print "%CPU " + cpu_result
    print "%MEM " + mem_result

    cmd_logperf = "echo " + operation + "," + cpu_result + "," + mem_result + " >> " + performancelog
    print cmd_logperf
    dut.execute(cmd_logperf)



#
# This function will unmount all mount point of a particular device. The directory of the moint 
# point will be removed as well
#
def unmount_all (device, testVerdict, testlog, dut, OS):

    if (OS == "fedora16"):
        cmd_search_mount_point = "df | grep " + device + " | awk '{print $6}'"
    elif (OS == "android"):
        cmd_search_mount_point = "adb shell df | grep " + device + " | awk '{print $6}'"

    print cmd_search_mount_point
    ret = dut.execute(cmd_search_mount_point)
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
            ret = dut.execute(cmd_unmount)

            rmdir (mount, testVerdict, dut, testlog, OS)

    ret = dut.execute(cmd_search_mount_point)
    if (ret == ""):
        print "All mount points has been unmounted"
        cmd_logging = "echo All mount points has been unmounted >> " + testlog
    else:
        print "Not all mount points has been unmounted"
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


#
# This function will return a string of random data in hexadecimal format. Input x number of bytes to 
# be generated and it will return a string of x hexadecimal characters
#

def reverse_binary(temp_data):

    data = bin(temp_data)[2:].zfill(8)
    source = BitStream('0b'+ data)
    num_list = []
    num = 0
    source.pos=0
    while num < 8:
        num_list.append(str(source.read('bin:1')))
        num += 1

    index = 0
    temp_string = ""
    #pop from list and insert into temp string
    while index < 8:
        temp = num_list.pop()
        if len(temp) == 1 :
            temp_string = temp_string + temp
        else:
            temp_string += temp
            temp_string += " "
        index += 1
    #format string to remove ' and convert to upper case
    temp_string = string.replace(temp_string, "'" , "")
    output = BitStream('0b'+temp_string)
    
    output_return = str(output.read('hex'))

    return output_return

def gen_random_hex(num_bytes, byte_length):

    num_list = []
    rev_list = []
    num = 1

    while num <= num_bytes:
        random_num_dec = random.randint(0,255)
        random_num_hex = hex(random_num_dec)[2:]
        random_num_bin = bin(random_num_dec)[2:].zfill(8)

        num_list.append(random_num_hex)
        rev_list.append(reverse_binary(random_num_dec))
        num += 1

    index = 0

    temp_string = ""
    rev_temp_string = ""

    temp_string_16 = ""
    rev_temp_string_16 = ""
    temp_string_16_split = ""
    rev_temp_string_16_split = ""

    temp_string_32 = ""
    rev_temp_string_32 = ""
    temp_string_32_split = ""
    rev_temp_string_32_split = ""

    #pop from list and insert into temp string
    while index < num_bytes:
        #pop for right list
        temp = num_list.pop()
        if len(temp) == 1 :
            temp_string = temp_string + "0" + temp + " "

            temp_string_16 = temp_string_16 + " 0" + temp + "0" + temp + " "
            temp_string_16_split = temp_string_16_split + " 0" + temp + " 0" + temp + " "

            temp_string_32 = temp_string_32 + " 0" + temp + "0" + temp + "0" + temp + "0" + temp + " "
            temp_string_32_split = temp_string_32_split + " 0" + temp + " 0" + temp + " 0" + temp + " 0" + temp + " "

        else:
            temp_string = temp_string + temp + " "

            temp_string_16 = temp_string_16 + temp + temp + " "
            temp_string_16_split = temp_string_16_split + temp + " " + temp + " "

            temp_string_32 = temp_string_32 + temp + temp + temp + temp + " "
            temp_string_32_split = temp_string_32_split + temp + " " + temp + " " + temp + " " + temp + " "


        #pop for reversed list
        temp = rev_list.pop()
        if len(temp) == 1 :
            rev_temp_string = rev_temp_string + "0" + temp + " "

            rev_temp_string_16 = rev_temp_string_16 + " 0" + temp + "0" + temp + " "
            rev_temp_string_16_split = rev_temp_string_16_split + " 0" + temp + " 0" + temp + " "

            rev_temp_string_32 = rev_temp_string_32 + " 0" + temp + "0" + temp + "0" + temp + "0" + temp + " "
            rev_temp_string_32_split = rev_temp_string_32_split + " 0" + temp + " 0" + temp + " 0" + temp + " 0" + temp + " "

        else:
            rev_temp_string = rev_temp_string + temp + " "

            rev_temp_string_16 = rev_temp_string_16 + temp + temp + " "
            rev_temp_string_16_split = rev_temp_string_16_split + temp + " " + temp + " "

            rev_temp_string_32 = rev_temp_string_32 + temp + temp + temp + temp + " "
            rev_temp_string_32_split = rev_temp_string_32_split + temp + " " + temp + " " + temp + " " + temp + " "

        index += 1
    #format string to remove ' and convert to upper case
    #for forward list
    temp_string = string.replace(temp_string, "'" , "")
    temp_string = string.upper(temp_string)

    temp_string_16 = string.replace(temp_string_16, "'" , "")
    temp_string_16 = string.upper(temp_string_16)
    temp_string_16_split = string.replace(temp_string_16_split, "'" , "")
    temp_string_16_split = string.upper(temp_string_16_split)

    temp_string_32 = string.replace(temp_string_32, "'" , "")
    temp_string_32 = string.upper(temp_string_32)
    temp_string_32_split = string.replace(temp_string_32_split, "'" , "")
    temp_string_32_split = string.upper(temp_string_32_split)

    #for reverse list
    rev_temp_string = string.replace(rev_temp_string, "'" , "")
    rev_temp_string = string.upper(rev_temp_string)

    rev_temp_string_16 = string.replace(rev_temp_string_16, "'" , "")
    rev_temp_string_16 = string.upper(rev_temp_string_16)
    rev_temp_string_16_split = string.replace(rev_temp_string_16_split, "'" , "")
    rev_temp_string_16_split = string.upper(rev_temp_string_16_split)

    rev_temp_string_32 = string.replace(rev_temp_string_32, "'" , "")
    rev_temp_string_32 = string.upper(rev_temp_string_32)
    rev_temp_string_32_split = string.replace(rev_temp_string_32_split, "'" , "")
    rev_temp_string_32_split = string.upper(rev_temp_string_32_split)

    print "MSB Data 8 bit        : " + temp_string

    print "MSB Data 16 bit       : " + temp_string_16
    print "MSB Data 16 bit split : " + temp_string_16_split

    print "MSB Data 32 bit       : " + temp_string_32
    print "MSB Data 32 bit split : " + temp_string_32_split

    print "LSB Data 8 bit        : " + rev_temp_string

    print "LSB Data 16 bit       : " + rev_temp_string_16
    print "LSB Data 16 bit split : " + rev_temp_string_16_split

    print "LSB Data 32 bit       : " + rev_temp_string_32
    print "LSB Data 32 bit split : " + rev_temp_string_32_split


    if byte_length == 8:
        return_string = temp_string + " :: " + rev_temp_string
    elif byte_length == 16:
        return_string = temp_string_16 + " :: " + temp_string_16_split + " :: " + rev_temp_string_16 + " :: " + rev_temp_string_16_split
    elif byte_length == 32:
        return_string = temp_string_32 + " :: " + temp_string_32_split + " :: " + rev_temp_string_32 + " :: " + rev_temp_string_32_split
    else:
        return_string = " "

    print return_string

    return return_string


