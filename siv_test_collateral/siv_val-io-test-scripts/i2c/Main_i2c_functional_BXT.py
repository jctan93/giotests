# Modified: 
# 27 January 2016, Kahu - Added -bl and -dma as dummy arguments to adapt with GIO
# - Added function kill_process(script_name),line number 157 to kill processes that are executed by aai2c_slave.py 
# - Modified the try expect on line 472
# - Added ("echo " + var + " >> /root/i2c.log" ) on line 84 of aai2c_slave.py test-app script, to log directly the data written by master into /root/i2c.log

import sys, os, re, argparse, time, Result_Parser, GenericCommand, getopt, string, common, socket, fcntl, struct
from ssh_util import *
from datetime import date, datetime

#default settings
dut_num = 1
osID = "linux_32"
read_write_mode = "read"
thm_report_path = "/root/I2C.report"
num_bytes = 8
slave_address = "aa"
speed = 100
gcs_port = 2300
test_type = "address"
dut_ip1 = "172.30.249.27"
keystroke_script = "/root/BXT_Daily_Automation/"

python_filename = sys.argv[0]
Usage = "I2C"
parser = argparse.ArgumentParser(prog = python_filename,description = Usage)
parser.add_argument('-ty', help='address - I2C-F002-M Valid I2C Address Testing / speed - I2C-F004-M Valid I2C Transaction Testing (For reporting only. Actual setting needs to be configured at driver load/boot time/dma - I2C-F006-N I2C DMA Support / valid_extended - I2C-F008-N I2C Valid Extended Configuration Test (use operation -wr auto)')
parser.add_argument('-r', help='<path_to_report_file>  Appends result to result file')
parser.add_argument('-os', help='android - For android testing - through USB Debug/adb connection / linux_32 - For generic 32 bit linux kernel testing / linux_64 - For generic 64 bit linux kernel testing')
parser.add_argument('-dev', help='<device_path> Specify the path to device here')
parser.add_argument('-wr', help='read - For Read Operation / write - For Write Operation / auto - For Auto Script Control') 
parser.add_argument('-bs', help='<num_bytes> Integer of 1 till 8 bytes')
parser.add_argument('-sa', help='<slave_address> Slave Address in hex, e.g. 20, 50, 2A, 120, 2FF, 3FF / 7 Bit Addressing - Valid range is 7 till 77 / 10 Bit Addressing - Valid range is 7 till 3FF')
parser.add_argument('-s', help='<speed> Valid I2C Transaction Speeds - Actual setting needs to be done at boot/driver load')
parser.add_argument('-c', help='<dut_num> See ip and aadvark_usb_port configuration - To support Multiple device connected to same THM ')
parser.add_argument('-g', help='<port> Generic command port')
parser.add_argument('-ip', help='<dut_ip1> IP address for target SUT')
parser.add_argument('-thm_ip', help='THM IP Address')
parser.add_argument('-pci', help='ACPI/PCI')
parser.add_argument('-bl', help='Bit lenght. E.g. 4, 8, 16, 32. Default is 8') # DUMMY FOR NOW
parser.add_argument('-dma', help='on or off') # DUMMY FOR NOW

### Get Argument ####
args = parser.parse_args()
if args.ty is not None:           
   test_type = str(args.ty)
if args.r is not None:           
     thm_report_path = str(args.r)
if args.os is not None:           
     osID = str(args.os)
if args.dev is not None:           
     dut_i2c_port = str(args.dev)
if args.wr is not None:           
     read_write_mode = str(args.wr)
if args.bs is not None:           
     num_bytes = int(args.bs)
if args.sa is not None:           
     slave_address = str(args.sa).lower()
if args.s is not None:           
	speed = str(int(args.s)/1000)		
if args.c is not None:           
     dut_num = int(args.c)        
if args.ip is not None:           
     dut_ip1 = str(args.ip)
if args.thm_ip is not None:           
	thm_ip = str(args.thm_ip)
if args.g is not None:           
     gcs_port = int(args.g)
if args.pci is not None:           
     pci = str(args.pci)

# define class parameter
pret = Result_Parser.Result_Parser()
ssh_agent = ssh_com(dut_ip1)
ssh_agent.setpub(sshpass="")
ssh_thm = ssh_com(thm_ip)
ssh_thm.setpub(sshpass="bxtroot")

#Test Machines Setup Parameters
aadvark_usb_port1 = 0
aadvark_usb_port2 = 1

#thm_setup
testlog_dir = "/root/IO_TESTS_LOG/I2C/" 

#Test Binaries Location Parameters
thm_avk_api_loc = "/home/siv_test_collateral/siv_val-io-test-apps/misc/aadvark-api-v5.15.2/linux-x86_64/python/"
thm_avk_i2cslave_script = "aai2c_slave.py"
thm_avk_aadetect_script = "aadetect.py"
thm_log = "/root/i2c.log"
thm_avk_gui_loc = ""
dut_app_loc = "/home/siv_test_collateral/siv_val-io-test-apps/i2c/" 
# for fedora application where dut is not connected through thm, path to app is relative to location of generic command server...
#dut_app = "/pch_i2c_sample_mod_10bit"
dut_app = "pch_i2c_sample"

#Test Specific Variables
thm_avk_api_timeout = 10000
min_address=5
max_address=300
min_bytes=1
max_bytes=8

#Kills all the ' script_name ' processes that are running
def kill_process(script_name):
	line_output = thm.execute("ps aux | awk '/" + script_name + "/ { print $2}'")
	splitter = re.compile("\n")
	read_list = splitter.split(line_output)
	for line in read_list:
		thm.execute("kill -9 " + line)
	print "[Debug] All '{0}' processes are killed".format(script_name)

#Lookup table for ConfigID
def configID_lookup (operation,test_type,num_byte,address,speed):
	
	temp=""
	if operation == "read":
		if test_type == "dma":
			temp = "03"
		else: temp = "01"
	elif operation == "write":
		if test_type == "dma":
			temp = "04"
		else: temp = "02"
	
	if len(address) == 1:
		temp = temp + str(num_byte) + "00" + str(address)
	elif len(address) == 2:
		temp = temp + str(num_byte) + "0" + str(address)
	elif len(address) == 3:
		temp = temp + str(num_byte) + str(address)
	
	if speed == "100":
		temp = temp + "02"
	elif speed == "400":
		temp = temp + "03"
	
	return temp

#Lookup table for TestID
def testID_lookup(test_type,configID):
	if test_type == "address":
		return "I2C-F002-M-" + configID + "\; Valid I2C Address Testing"
	elif test_type == "speed":
		return "I2C-F004-M-" + configID + "\; Valid I2C Transaction Speed Testing"
	elif test_type == "dma":
		return "I2C-F006-N-" + configID + "\; I2C DMA Support"
	elif test_type == "valid_extended":
		return "I2C-F008-N-" + configID + "\; I2C Valid Extended Configuration Testing"
	else :
		print "[ERROR] - Invalid Test Type"
		sys.exit(1)


#List Available Aadvark Devices
def detect_aadvark_port():
	os.system("python " + aardvark_api_loc + thm_avk_aadetect_script)
	return 0

#DUT Read from Aadvark
def i2c_read(port, slave, num_bytes, full_data, testVerdict,osID):

	temp_list_splitter = re.split ( ":: ", full_data )
	forward_data = temp_list_splitter[0]
	reverse_data = temp_list_splitter[1]
	
	data = forward_data
	
	cmd_remove_thmlog = "rm " + thm_log
	print "[DEBUG] Clean: " + cmd_remove_thmlog
	thm.execute(cmd_remove_thmlog)
	
	slave_int = int(slave,16)
	
	if slave_int <= 119: #set default to 7 bit address
		print "Address Range between 0x00 and 0x77"
		slave_api_send = slave
	
	elif slave_int > 119 and slave_int <= 255: #if larger than 0x77
		print "Address Range between 0x78 and 0xFF"
		append_hex = slave
		slave_api_send = "78"
	
	
	elif slave_int > 255 and slave_int <= 511: #if larger than 0xFF
		print "Address Range between 0x100 and 0x1FF"
		temp_hex=str(hex(int(slave,16)-256))
		trunk=re.search("(?<=x)\w+",temp_hex)
		append_hex = trunk.group(0)
		slave_api_send = "79"
	
	elif slave_int > 511 and slave_int <= 767: #if larger than 0x1FF
		print "Address Range between 0x200 and 0x2FF"
		temp_hex=str(hex(int(slave,16)-512))
		trunk=re.search("(?<=x)\w+",temp_hex)
		append_hex = trunk.group(0)
		slave_api_send = "7A"
	
	elif slave_int > 767 and slave_int <= 1023: #if larger than 0x2FF
		print "Address Range between 0x300 and 0x3FF"
		temp_hex=str(hex(int(slave,16)-768))
		trunk=re.search("(?<=x)\w+",temp_hex)
		append_hex = trunk.group(0)
		slave_api_send = "7B"
	
	else:
		print "TEST ERROR Address Larger than 0x3FF is invalid... Exiting..."
		thm.execute("echo TEST ERROR Address Larger than 0x3FF is invalid... Exit Test " + " >> " + testlog_loc)
		test_result = False
		sys.exit(1)
	
	#send python command in format "python <python.py> <aadvark_port> <slave_address_hex> <timeout_ms> <num_bytes> <data>" stdout redirected to log_file and terminal
	cmd_execute_api = "python " + str(thm_avk_api_loc) + str(thm_avk_i2cslave_script) +  " " + str(port) + \
					 " 0x0" + str(slave_api_send) + " " + str(thm_avk_api_timeout) + " " + str(num_bytes) + " " + \
					 str(data) + " 2>&1 | tee " + str(thm_log)
	
	print "[DEBUG] API COMMAND: " + cmd_execute_api
	cmd_logging = "echo " + cmd_execute_api + " >> " + testlog_loc
	thm.execute(cmd_logging)
	
	time.sleep(1)
	thm.timeexecute(cmd_execute_api)
	
	time.sleep(1)
	#command dut to execute app in format " ./<app> </dev/i2c-port> <slave_address> and collect app stdout
	
	if osID.upper() == "ANDROID":
		 cmd_i2c_app_read = "adb shell ." + str(dut_app_loc) + "android" + str(dut_app)+ " " + str(dut_i2c_port) + " " + str(slave)
	elif osID.upper() == "LINUX_64":
		 cmd_i2c_app_read = str(dut_app_loc) + str(dut_app) + " " + str(dut_i2c_port) + " " + str(slave)
	elif osID.upper() == "LINUX_32":
		 cmd_i2c_app_read = str(dut_app_loc) + str(dut_app) + " " +	str(dut_i2c_port) + " " + str(slave)
	
	print "[DEBUG] READ COMMAND: " + cmd_i2c_app_read
	cmd_logging = "echo " + cmd_i2c_app_read + " >> " + testlog_loc
	thm.execute(cmd_logging)
	
	#for android, dut is accessed through thm. Otherwise, need to command to dut directly.
	if osID.upper() == "ANDROID":
		read_app_output = thm.execute(cmd_i2c_app_read)
	else:
		read_app_output = dut.execute(cmd_i2c_app_read)
	
	print "[DEBUG] Read Output: " + read_app_output
	cmd_logging = "echo " + read_app_output + " >> " + testlog_loc
	thm.execute(cmd_logging)
	
	#format expected data to be lower case with no spaces
	expected_data = string.replace(data, " " , "")
	expected_data = string.lower(expected_data)
	aadvark_data=""
	  
	splitter = re.compile("\n")
	read_list = splitter.split(read_app_output)
	
	#search and strip data line by line and find data read by aadvark    
	try:
		for line in read_list:
			if re.search("data=" ,line):
				parsed = re.search("(?<=data\D)\w+", str(line))
				initial_data = parsed.group(0).lstrip()
				aadvark_data += initial_data
				if len(aadvark_data) == (num_bytes * 2):  #check to length of expected data
					break
	
	except:
		aadvark_data=""
	
	
	print "[DEBUG] Expected Data: " + expected_data
	cmd_logging = "echo Expected Data: " + expected_data + " >> " + testlog_loc
	thm.execute(cmd_logging)
	
	print "[DEBUG] Read Data: " + aadvark_data
	cmd_logging = "echo Read Data: " + aadvark_data + " >> " + testlog_loc
	thm.execute(cmd_logging)
	
	time.sleep(3)
	
	#compare data and set result        
	if aadvark_data == expected_data:
		if testVerdict == True:
			testVerdict = True
		write_result = True
		thm.execute("echo DUT Read 0x0" + str(slave) + " expected=" + expected_data + " aadvark_data=" + aadvark_data + " >> " + testlog_loc)
		
	else:
		testVerdict = False
		thm.execute("echo DATA Received Check Failed on Host Machine, DUT Read 0x0" + str(slave) + " expected=" + expected_data + " aadvark_data=" + aadvark_data + " >> " + testlog_loc)
	
	print "[DEBUG] Clean: " + cmd_remove_thmlog
	cmd_logging = "echo " + cmd_remove_thmlog + " >> " + testlog_loc
	thm.execute(cmd_logging)
	
	thm.execute(cmd_remove_thmlog)
	kill_process(thm_avk_i2cslave_script)
	
	return testVerdict


#DUT Write to Aadvark
def i2c_write(port, slave, num_bytes , full_data, testVerdict, osID):
	
	temp_list_splitter = re.split ( ":: ", full_data )
	forward_data = temp_list_splitter[0]
	reverse_data = temp_list_splitter[1]
	
	data = forward_data
	
	cmd_remove_thmlog = "rm " + thm_log
	print "[DEBUG] Clean: " + cmd_remove_thmlog
	thm.execute(cmd_remove_thmlog)
	
	slave_int = int(slave,16)
	
	if slave_int <= 119: #set default to 7 bit address
		print "Address Range between 0x00 and 0x77"
		slave_api_send = slave
	
	elif slave_int > 119 and slave_int <= 255: #if larger than 0x77
		print "Address Range between 0x78 and 0xFF"
		append_hex = slave
		slave_api_send = "78"    
	
	elif slave_int > 255 and slave_int <= 511: #if larger than 0xFF
		print "Address Range between 0x100 and 0x1FF"
		temp_hex=str(hex(int(slave,16)-256))
		trunk=re.search("(?<=x)\w+",temp_hex)
		append_hex = trunk.group(0)
		slave_api_send = "79"
	
	elif slave_int > 511 and slave_int <= 767: #if larger than 0x1FF
		print "Address Range between 0x200 and 0x2FF"
		temp_hex=str(hex(int(slave,16)-512))
		trunk=re.search("(?<=x)\w+",temp_hex)
		append_hex = trunk.group(0)
		slave_api_send = "7A"
	
	elif slave_int > 767 and slave_int <= 1023: #if larger than 0x2FF
		print "Address Range between 0x300 and 0x3FF"
		temp_hex=str(hex(int(slave,16)-768))
		trunk=re.search("(?<=x)\w+",temp_hex)
		append_hex = trunk.group(0)
		slave_api_send = "7B"
	
	else:
		print "TEST ERROR Address Larger than 0x3FF is invalid... Exiting..."
		thm.execute("echo TEST ERROR Address Larger than 0x3FF is invalid... Exit Test " + " >> " + testlog_loc)
		test_result = False
		sys.exit(1)
	
	# if append_hex == "0":
	#	append_hex = "00"
	
	#send python command in format "python <python.py> <aadvark_port> <slave_address_hex> <timeout_ms> <num_bytes> <data>" stdout redirected to log_file and terminal
	
	
	cmd_execute_api = "python " + str(thm_avk_api_loc) + str(thm_avk_i2cslave_script) +  " " + str(port) + \
					 " 0x0" + str(slave_api_send) + " " + str(thm_avk_api_timeout) + " " + str(num_bytes) + " " + \
					 str(data) 
	
	print "[DEBUG] API COMMAND: " + cmd_execute_api
	cmd_logging = "echo " + cmd_execute_api + " >> " + testlog_loc
	thm.execute(cmd_logging)
	
	thm.timeexecute(cmd_execute_api)
	
	time.sleep(2)
	#command dut to execute app in format " ./<app> </dev/i2c-port> <slave_address> <write_data_bytes>
	if osID.upper() == "ANDROID":
		 cmd_i2c_app_write = "adb shell ." + str(dut_app_loc) + "android" + str(dut_app) + " " + str(dut_i2c_port) + " " + str(slave) + " " + str(data)
	elif osID.upper() == "LINUX_64":
		 cmd_i2c_app_write = str(dut_app_loc) + str(dut_app) + " " + str(dut_i2c_port) + " " + str(slave) + " " + str(data)
	elif osID.upper() == "LINUX_32":
		 cmd_i2c_app_write = str(dut_app_loc) + str(dut_app) + " " + str(dut_i2c_port) + " " + str(slave) + " " + str(data)
	
	print "[DEBUG] WRITE COMMAND: " +  cmd_i2c_app_write
	cmd_logging = "echo " + cmd_i2c_app_write + " >> " + testlog_loc
	thm.execute(cmd_logging)
	
	#for android, dut is accessed through thm. Otherwise, need to command to dut directly.
	if osID.upper() == "ANDROID":
		thm.execute(cmd_i2c_app_write)
	else:
		dut.execute(cmd_i2c_app_write)
	
	#format expected data to be lower case with no spaces
	expected_data = string.replace(data, " " , "")
	expected_data = string.lower(expected_data)
	if slave_int > 119: #if greater than 0x77, append address to first byte
		expected_data = append_hex + expected_data
	aadvark_data=""
	
	time.sleep(3)
	
	cmd_cat_thmlog = "cat " + thm_log
	print "[DEBUG] Write Output: " +  cmd_cat_thmlog
	cmd_logging = "echo " + cmd_cat_thmlog + " >> " + testlog_loc
	thm.execute(cmd_logging) 
	
	result = thm.execute(cmd_cat_thmlog)
	
	#print "[DEBUG] Result: " +  result
	#split to list based on splitter "newline"
	splitter = re.compile("\n")
	write_list = splitter.split(result)
	
	
	#search line by line for expected data and strip white spaces
	try:
		i = 0
		for line in write_list:
			#if i > 1:
			#    aadvark_data += line
			aadvark_data += line
			i=i+1
			if aadvark_data == expected_data:
				break
	except:
		aadvark_data=""
	
	print "[DEBUG] Expected Data: " + expected_data
	cmd_logging = "echo Expected Data: " + expected_data + " >> " + testlog_loc
	thm.execute(cmd_logging)
	
	print "[DEBUG] Write Data: " + aadvark_data
	cmd_logging = "echo Write Data: " + aadvark_data + " >> " + testlog_loc
	thm.execute(cmd_logging)
	
	
	#compare data and set result        
	if aadvark_data == expected_data:
		if testVerdict == True:
			testVerdict = True
		write_result = True
		thm.execute("echo DUT Write 0x0" + str(slave) + " expected=" + expected_data + " aadvark_data=" + aadvark_data + " >> " + testlog_loc)
		
	else:
		testVerdict = False
		thm.execute("echo DATA Received Check Failed on Host Machine, DUT Write 0x0" + str(slave) + " expected=" + expected_data + " aadvark_data=" + aadvark_data + " >> " + testlog_loc)
	
	print "[DEBUG] Clean: " + cmd_remove_thmlog
	cmd_logging = "echo " + cmd_remove_thmlog + " >> " + testlog_loc
	thm.execute(cmd_logging)
	
	thm.execute(cmd_remove_thmlog)
	kill_process(thm_avk_i2cslave_script)
	
	return testVerdict

# Start of MainFunction
if speed == "100":
	ssh_agent.ssh_exec("reboot")
	time.sleep(10)
	ssh_thm.ssh_exec("python " + keystroke_script + "keystroke.py -setting i2c_standard_mode")
	time.sleep(60)

currentDate = common.get_date()  # get today's date
Time_now = common.get_current_time() # get current time
date_time = currentDate + "_" + Time_now  #form timestamp

testlog_dir = testlog_dir + str(currentDate) + "_"+ str(dut_num) +"/"
testlog_loc = testlog_dir + str(test_type) + "_" + str(date_time) + "_" + str(dut_num) + ".log"

print "\n[DEBUG] Log Location: " + testlog_loc
print "\n[DEBUG] Test Suite: " + test_type

if thm_avk_api_loc == "":
	thm_avk_api_loc = "/root/aardvark-api-linux-i686-v5.13"

test_result = True

#This switch is to enable multiple DUT to be tested with a single THM.
#use aadetect.py in /test-apps/misc/aadvark-api-v5.13/linux_32/python
if dut_num == 1:
	dut_ip = dut_ip1
	aadvark_usb_port = aadvark_usb_port1
elif dut_num == 2:
	dut_ip = dut_ip2
	aadvark_usb_port = aadvark_usb_port2
else:
	sys.exit(1)

if ssh_agent.chk_con():
	try:
		if osID.upper() == "ANDROID":
			thm = GenericCommand.GenericCommand()
			thm.login(thm_ip,gcs_port)
			print "\n"
			thm.execute("adb devices")		
			thm.execute("mkdir -p " + testlog_dir)		
		else:
			thm = GenericCommand.GenericCommand()
			thm.login(thm_ip,gcs_port)
			thm.execute("mkdir -p " + testlog_dir)		
			dut = GenericCommand.GenericCommand()
			dut.login(dut_ip,gcs_port)
		
		# Temporary solution for latest kernel
		dut_i2c_port = "/dev/i2c-3"
		### added by William
		# ldata = str(dut.execute("i2cdetect -l | grep -i 'Synopsys DesignWare I2C adapter' | grep -v part | awk '{split($1,a); print a[1]}'"))
		# if ldata != "":
		# 	splitter = re.compile("\n")
		# 	dut_i2c_port = "/dev/" + splitter.split(ldata)[3]
		# 	print "I2C Port Used : " + dut_i2c_port
		executed_command = str(python_filename) + " -ty " + str(test_type) + " -r " + str(thm_report_path) + " -os " + str(osID) + " -dev " + str(dut_i2c_port) + " -wr " + str(read_write_mode) + " -bs " + str(num_bytes) + " -a " + str(slave_address) + " -s " + str(speed) + " -c " + str(dut_num) + " -g " + str(gcs_port) 
		print "\n[DEBUG] Executed Command: " + str(executed_command)
		print "[DEBUG] THM IP Used : " + str(thm_ip)
		print "[DEBUG] DUT IP Used :" + str(dut_ip)
		print "[DEBUG] Aadvark USB Port Used :" + str(aadvark_usb_port) + "\n"
		
		if test_type.upper() == "VALID_EXTENDED":		
			thm.execute("echo [I2C_RESULT]======================================= " + " >> " + testlog_loc)
			thm.execute("echo [I2C_RESULT] Start: `date` " + " >> " + testlog_loc)
			thm.execute("echo [I2C_RESULT]======================================= " + " >> " + testlog_loc)
			curr_address=min_address
			curr_byte=min_bytes
			curr_loop_verdict=True
			overall_verdict=True			
			try:
				while curr_address <= max_address: #Outer while loop is for looping through address incrementally
					thm.execute("echo [I2C_RESULT]======================================= " + " >> " + testlog_loc)
					print "======================================="
					thm.execute("echo [I2C_RESULT]Current Address: " + str(curr_address) + " >> " + testlog_loc)
					print "Current Address: " + str(curr_address)
					curr_byte = min_bytes
					curr_loop_verdict=True
					try:
						while curr_byte <= max_bytes: #Outer while loop is for looping through bytes incrementally
							internal_loop_verdict = False
							testVerdict = True
							
							#Actual test starts here
							data = common.gen_random_hex(int(curr_byte), 8)
							internal_loop_verdict = i2c_read(aadvark_usb_port, str(curr_address), int(curr_byte) , data, testVerdict, osID)
							temp_configID =  configID_lookup ("read",str(test_type),str(curr_byte),str(curr_address),str(speed))
							if internal_loop_verdict == True:
								  internal_loop_verdict_out= "Pass"
								  thm.execute("echo " + str(dut_i2c_port) + " \;" + testID_lookup(test_type,temp_configID) + " \;" + "read" + " \;" + str(curr_byte) + " \;" + str(curr_address) + " \;" + str(speed) + " \; PASS"  + " >> " + thm_report_path)
							else:
								  internal_loop_verdict_out= "Fail"     
								  thm.execute("echo " + str(dut_i2c_port) + " \;" + testID_lookup(test_type,temp_configID) + " \;" + "read" + " \;" + str(curr_byte) + " \;" + str(curr_address) + " \;" + str(speed) + " \; FAIL"  + " >> " + thm_report_path)             

							thm.execute("echo [I2C_RESULT]Read Current Bytes: " + str(curr_byte) + " -- " + str(internal_loop_verdict_out) + " >> " + testlog_loc)
							print "    Read Current Bytes: " + str(curr_byte) + " -- " + str(internal_loop_verdict_out)

							curr_loop_verdict = curr_loop_verdict and internal_loop_verdict

							internal_loop_verdict = False
							testVerdict = True

							data = common.gen_random_hex(int(curr_byte), 8)
							internal_loop_verdict = i2c_write(aadvark_usb_port, str(curr_address), int(curr_byte) , data, testVerdict, osID)
							temp_configID =  configID_lookup ("write",str(test_type),str(curr_byte),str(curr_address),str(speed))
		
							if internal_loop_verdict == True:
								  internal_loop_verdict_out= "Pass"
								  thm.execute("echo " + str(dut_i2c_port) + " \;" + testID_lookup(test_type,temp_configID) + " \;" + "write" + " \;" + str(curr_byte) + " \;" + str(curr_address) + " \;" + str(speed) + " \; PASS"  + " >> " + thm_report_path)
							else:
								  internal_loop_verdict_out= "Fail"
								  thm.execute("echo " + str(dut_i2c_port) + " \;" + testID_lookup(test_type,temp_configID) + " \;" + "write" + " \;" + str(curr_byte) + " \;" + str(curr_address) + " \;" + str(speed) + " \; FAIL"  + " >> " + thm_report_path)                 
		
							thm.execute("echo [I2C_RESULT]Write Current Bytes: " + str(curr_byte) + " -- " + str(internal_loop_verdict_out) + " >> " + testlog_loc)
							print "    Write Current Bytes: " + str(curr_byte) + " -- " + str(internal_loop_verdict_out)

							curr_loop_verdict = curr_loop_verdict and internal_loop_verdict

							overall_verdict = overall_verdict and curr_loop_verdict
							#Actual test ends here
							curr_byte=curr_byte + 1
						thm.execute("echo [I2C_RESULT]======================================= " + " >> " + testlog_loc)
						print "======================================="
						if curr_loop_verdict == True:
							curr_loop_verdict_out= "PASSED"
						else:
							curr_loop_verdict_out= "FAILED"
						thm.execute("echo [I2C_RESULT]Address Test: " + str(curr_address) + " -- " + str(curr_loop_verdict_out) + " >> " + testlog_loc)      
						print "Address Test: " + str(curr_address) + " -- " + str(curr_loop_verdict_out)
						curr_address=curr_address + 1
					except StandardError, e:
						thm.execute("echo ERROR: Terminated in Data Bytes Loop " + str(e) + " >> " + testlog_loc)
						print "ERROR: Terminated in Data Bytes Loop" + str(e)
						sys.exit(1)
				thm.execute("echo [I2C_RESULT]======================================= " + " >> " + testlog_loc)
				print "======================================="
				if overall_verdict == True:
					test_result == True
					overall_verdict_out= "PASSED"
					sys.exit(0)
				else:
					test_result == False
					overall_verdict_out= "FAILED"   
					sys.exit(1)
				thm.execute("echo Final Verdict -- " + str(overall_verdict_out) + " >> " + testlog_loc)
				print "Final Verdict -- " + str(overall_verdict_out)
				thm.execute("echo [I2C_RESULT]======================================= " + " >> " + testlog_loc)
				thm.execute("echo [I2C_RESULT] End: `date` " + " >> " + testlog_loc)
				thm.execute("echo [I2C_RESULT]======================================= " + " >> " + testlog_loc)
			except StandardError, e:
				thm.execute("echo ERROR: Terminated in Address Loop " + str(e) + " >> " + testlog_loc)
				print "echo ERROR: Terminated in Address Loop" + str(e)
				sys.exit(1)		
		else:
			print "\nRead/Write Mode: " + read_write_mode 
			thm.execute("echo Read/Write Mode: " + str(read_write_mode) + " >> " + testlog_loc)
			print "Num Bytes: " + str(num_bytes) + "\n"
			thm.execute("echo Num Bytes: " + str(num_bytes) + " >> " + testlog_loc)
			data = ""
			data = common.gen_random_hex(int(num_bytes), 8)
			print "\nData: " + data
			thm.execute("echo Data     : " + data + " >> " + testlog_loc)
			print "Slave Address: " + str(slave_address)
			thm.execute("echo Slave Address: " + str(slave_address) + " >> " + testlog_loc)
			print "Speed: " + str(speed)+ "\n"
			thm.execute("echo Speed: " + str(speed) + " >> " + testlog_loc)
			testVerdict = True
			test_result = False
			
			if read_write_mode.upper() == "READ":
				test_result= i2c_read(aadvark_usb_port, slave_address, int(num_bytes) , data, testVerdict, osID)
			elif read_write_mode.upper() == "WRITE":
				test_result = i2c_write(aadvark_usb_port, slave_address, int(num_bytes) , data, testVerdict, osID)
			else:
				test_result = False
			
			temp_configID =  configID_lookup (str(read_write_mode),str(test_type),str(num_bytes),str(slave_address),str(speed))
			print testID_lookup(test_type,temp_configID)
			
			# revert back to fast mode
			if speed == "100":
				ssh_agent.ssh_exec("reboot")
				time.sleep(10)
				ssh_thm.ssh_exec("python " + keystroke_script + "keystroke.py -setting i2c_fast_mode")
				time.sleep(60)
			if ssh_agent.chk_con():
				if test_result == True: 
					print "\n[VERDICT] I2C Test Pass!!"
					thm.execute("echo I2C Test Pass!! >> " + testlog_loc)
					thm.execute("echo " + str(dut_i2c_port) + " \;" + testID_lookup(test_type,temp_configID) + " \;" + str(read_write_mode) + " \;" + str(num_bytes) + " \;" + str(slave_address) + " \;" + str(speed) + " \; PASS"  + " >> " + thm_report_path)
					sys.exit(0)
				else:
					print "\n[VERDICT] Test Fail!!"
					thm.execute("echo " + str(dut_i2c_port) + " \;" + testID_lookup(test_type,temp_configID) + " \;" + str(read_write_mode) + " \;" + str(num_bytes) + " \;" + str(slave_address) + " \;" + str(speed) + " \; FAIL"  + " >> " + thm_report_path)
					sys.exit(1)
	except StandardError, e:
		thm.execute("echo TEST ERROR " + str(e) + " >> " + testlog_loc)
		test_result = False
		sys.exit(1)