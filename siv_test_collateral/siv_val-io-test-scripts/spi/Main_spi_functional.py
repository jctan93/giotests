import sys
import os
import re
import time
import argparse
#import Result_Parser
from datetime import date, datetime
import GenericCommand
import getopt
import common
import string
import os

#Usage : <this_script.py> -t <test_case_ID> -r <project_ID> -o <DUT_OS> -m <dut_read/write> -b <num_bytes> -c <bit_order> -l <bit_length> -e <mode> -a <slave_address> -s <speed> -d <dma_on/off> -z <auto> -f <dut_num>
# -o [android|linux_64|linux_32] # [android|fedora14_64|fedora16_32] 
# -wr [read|write]
# -b [integer of 1 till 8 bytes]
# -c [msb|lsb] first
# -l [8|16|32]
# -e [0|1|2|3] SPI Modes
# -a [slave address in hex, e.g. 20, 50, 2A] - Use 50 as default. To be removed next revision.
# -s 25000
#    75000
#    125000
#    250000
#    500000
#    750000
#    800000
#    1000000
#    2000000
# -d [on|off] 

# PORTIONS BELOW ARE OBSOLETE
# -z -> auto (runs incrementally for speeds specified in lookup table
#               ->for each speed test modes 0 to 3
#                    -> for each mode test bitoder msb and lsb
#                          -> for each bitorder test bit length 8, 16, 32
#                                -> for each speed and mode test 1 to 8 data bytes long  
# -f [dut_num] see ip and aadvark_usb_port configuration. 

#pret = Result_Parser.Result_Parser()

#Test Machines Setup Parameters
aadvark_usb_port1 = 0
testlog_dir = "/root/IO_TESTS_LOG/SPI/"

#Test Binaries Location Parameters
avk_api_loc = "/home/siv_test_collateral/siv_val-io-test-apps/misc/aadvark-api-v5.15.2/linux-x86_64/python/"
avk_spislave_script = "aaspi_slave.py"
avk_aadetect_script = "aadetect.py"
avk_log = "/root/spi.log"
avk_gui_loc = ""
dut_app_loc = "/home/siv_test_collateral/siv_val-io-test-apps/spi/"
# for fedora application where dut is not connected through thm, path to app is relative to location of generic command server...
dut_app = "pch_spi_sample"

#Test Specific Variables
avk_timeout = 50000
dut_spi_port = "/dev/spidev3.0"

#For Auto Loop testing
min_speed_index=0
max_speed_index=3
min_mode=0
max_mode=3
min_bitorder_index=1
max_bitorder_index=1
min_bitlength_index=1
max_bitlength_index=2
min_bytes=1
max_bytes=8

#List variable
script_name = str(sys.argv[0])
testID = "SPI_TEST" # Self Defined
projectID = "vlv2" # Self Defined
osID = "linux_32" #  
read_write_mode = "write"
num_bytes =32
bitorder = "msb" 
bitlength = 8
mode = 0 ## 
slave_address = 50
speed = 25000
dma = "off"
suite = "off"
tool = "EEPROM" ## aardvark / EEPROM
dut_num = 1 ## 1 / 2
pci = "undefined"
chip_select = 1
negative_test = False

## THIS PART OF THE SCRIPT GET THE COMMAND LINE PARAMETERS

usage = "This script runs both SPI and High Speed SPI with aardvark test tool or EEPROM"

parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-ip', help='IP address for target SUT')
parser.add_argument('-thm_ip', help='THM IP address ')
parser.add_argument('-wr', help='Read or Write mode [read|write]')
parser.add_argument('-t', help='Tool. [aardvark|EEPROM]')
parser.add_argument('-bs', help='Bytes size [1-8]')
parser.add_argument('-bo', help='Bit Oder, [msb|lsb]')
parser.add_argument('-pci', help='PCI or ACPI mode. [pci|acpi]')
parser.add_argument('-m', help='Signal Mode [0|1|2|3]')
parser.add_argument('-s', help='Transfer Rate [25000|75000|125000|250000|500000|750000|800000|1000000|2000000|5000000|10000000]. Aardvark does not support speeds beyond 250kbps')
parser.add_argument('-os', help='osID [android|linux_32|linux_64]')
parser.add_argument('-dma', help='DMA Mode [on|off]')
parser.add_argument('-bl', help='Bit length [8|16|32]')
parser.add_argument('-p', help='SPI Port. Default for PCI mode = /dev/spidev0.0')
parser.add_argument('-cs', help='Chip Select. Default = 1 [int]')
parser.add_argument('-neg', help='Negative Test mode [on|off]')

args = parser.parse_args()

if args.ip is not None:
   dut_ip1 = str(args.ip)
if args.thm_ip is not None:
   thm_ip = str(args.thm_ip)
if args.wr is not None:
   read_write_mode = args.wr
if args.t is not None:
   tool = str(args.t)
if args.bs is not None:
   num_bytes = int(args.bs)
if args.bo is not None:
   bitorder = str(args.bo)
if args.m is not None:
   mode = int(args.m)
if args.s is not None:
   speed = str(args.s)
if args.pci is not None:
   pci = str(args.pci)
if args.os is not None:
   osID = str(args.os)
if args.dma is not None:
   dma = str(args.dma)
if args.bl is not None:
   bitlength = int(args.bl)
if args.p is not None:
   dut_spi_port = str(args.p)
if args.cs is not None:
   chip_select = str(args.cs)
if args.neg is not None:
   negate = str(args.neg)
   if negate.upper() == "ON":
       negative_test = True


## CHECKING THE SANITY FOR AARDVARK TOO SELECTION
if tool.upper() == "AARDVARK" and int(speed) > 250000:
    print "Error: Invalid speed for Aardvark tool. Does not support speed beyond 250kbps"
    sys.exit(1)

## SETTING PORT BASED ON PCI AND CHIP SELECT 
if args.p is None and args.pci is not None:
    if pci.upper() == "PCI":
        spi_port_1 = "0"
    elif pci.upper() == "ACPI":
        spi_port_1 = "32766"
    else:
        print "Error: Unable to set SPI port. Unable to determine PCI mode."
        sys.exit(1)

    spi_port_2 = str(int(chip_select)-int(1))
    dut_spi_port = "/dev/spidev" + spi_port_1 + "." + spi_port_2

elif args.p is None and args.pci is None:
    print "Error: SPI port not defined."
    sys.exit(1)


## TEST LOG NAMING AND DIRECTORY

currentDate = common.get_date()  # get today's date
Time_now = common.get_current_time() # get current time
date_time = currentDate + "_" + Time_now  #form timestamp
testlog_dir = testlog_dir + str(currentDate) + "_"+ str(dut_num) +"/"
if tool.upper() == "AARDVARK": ## LOG NAME FOR AARDVARK TOOL
    testlog_loc = testlog_dir + str(testID) + "_" + str(date_time) + "_" + str(dut_num) + "_" + str(read_write_mode) + "_" + str(num_bytes) + "_" + str(bitorder) + "_" + str(bitlength) + "_" + str(mode) + "_" + str(speed) + "_" + str(dma) + "_" + str(tool) + "_" + str(pci)  + ".log"
else: ## LOG NAME FOR EEPROM TOOL
    testlog_loc = testlog_dir + str(testID) + "_" + str(date_time) + "_" + str(dut_num) + "_readwrite_" + str(num_bytes) + "_" + str(bitorder) + "_" + str(bitlength) + "_0_" + str(speed) + "_" + str(dma) + "_EEPROM_" + str(pci)  + ".log"
    

try:

    if osID.upper() == "ANDROID":
    
		thm = GenericCommand.GenericCommand()
		thm.login(thm_ip)

		thm.execute("adb devices")
		
		thm.execute("mkdir -p " + testlog_dir)
             
    else:
              
		thm = GenericCommand.GenericCommand()
		thm.login(thm_ip)
	 
		thm.execute("mkdir -p " + testlog_dir)
		dut = GenericCommand.GenericCommand()
		dut.login(dut_ip1)
           
except StandardError, e:
	thm.execute("echo TEST ERROR " + str(e) + " >> " + testlog_loc)
	test_result = False
	sys.exit(1)			

if tool == "aardvark":

	#List Available Aadvark Devices
	def detect_aadvark_port():
		os.system("python " + aardvark_api_loc + avk_aadetect_script)
		return 0


	#Lookup table for speed
	def speed_lookup(index_num):

		if index_num == 1:
			return 25000
		elif index_num == 2:
			return 75000
		elif index_num == 3:
			return 125000
		elif index_num == 4:
			return 250000
		elif index_num == 5:
			return 500000
		elif index_num == 6:
			return 750000
		elif index_num == 7:
			return 800000
		elif index_num == 8:
			return 1000000
		elif index_num == 9:
			return 2000000
		else:
			return 25000
		
	#Lookup table for bit ordering
	def bitorder_lookup(index_num):

		if index_num == 1:
			return "msb"
		elif index_num == 2:
			return "lsb"
		else:
			return "msb"
		
	#Lookup table for bit length
	def bitlength_lookup(index_num):

		if index_num == 1:
			return 8
		elif index_num == 2:
			return 16
		elif index_num == 3:
			return 32
		else:
			return 8

	#DUT Read from Aadvark
	def spi_read(port, bytesize, speed, mode, order, slave, num_bytes, full_data, testVerdict, osID):

		temp_list_splitter = re.split ( ":: ", full_data )

		#the aadvark API only accepts 8 bit long bytes. Thus, we workaround by using two 8 bit bytes which is read by dut as single 16 bit byte.
		if bytesize == 8:
			forward_data = temp_list_splitter[0]
			reverse_data = temp_list_splitter[1]

			api_data = forward_data
			app_data = forward_data

			api_num_bytes = num_bytes

		elif bytesize == 16:
			forward_data = temp_list_splitter[0]
			forward_data_8bit = temp_list_splitter[1] #this is the 16 bit split to 8 bit chunks.
			reverse_data = temp_list_splitter[2]

			api_data = "00 00 " + forward_data_8bit #pad the header bytes"
			app_data = forward_data

			api_num_bytes = num_bytes * 2

		elif bytesize == 32:
			forward_data = temp_list_splitter[0]
			forward_data_8bit = temp_list_splitter[1] #this is the 16 bit split to 8 bit chunks.
			reverse_data = temp_list_splitter[2]

			api_data = "00 00 00 00 00 00 " + forward_data_8bit
			app_data = forward_data

			api_num_bytes = num_bytes * 4


		cmd_remove_thmlog = "rm " + avk_log
		print cmd_remove_thmlog
		thm.execute(cmd_remove_thmlog)

		#send python command in format "python <python.py> <aadvark_port> <mode> <bitorder> <slave_address_hex> <timeout_ms> <num_bytes> <data>" stdout redirected to log_file and terminal
		cmd_execute_api = "python " + str(avk_api_loc) + str(avk_spislave_script) +  " " + str(port) + \
						 " " + str(mode) + " " + str(order) + " 0x0" + str(slave) + " " + str(avk_timeout) + \
						 " " + str(bytesize) + " " + str(api_num_bytes) + " " + str(api_data) + \
						 " 2>&1 | tee " + str(avk_log)
	 
		print cmd_execute_api
		cmd_logging = "echo " + cmd_execute_api + " >> " + testlog_loc
		thm.execute(cmd_logging)

		time.sleep(1)
		thm.timeexecute(cmd_execute_api)

		time.sleep(1)
		#command dut to execute app in format " ./<app> </dev/spidev-port> <bytesize> <speed> <bitorder> <mode> <slave_address> and collect app stdout
	   
		if osID.upper() == "ANDROID":
			cmd_spi_app_read = "adb shell ." + str(dut_app_loc) + "android" + str(dut_app) + " " + \
							   str(dut_spi_port) + " " + str(bytesize) + " " + str(speed) + " " + \
							   str(order) + " " + str(mode) + " " + str(slave)
		elif osID.upper() == "LINUX_64":
			cmd_spi_app_read = str(dut_app_loc) + str(dut_app) + " " + \
							   str(dut_spi_port) + " " + str(bytesize) + " " + str(speed) + " " + \
							   str(order) + " " + str(mode) + " " + str(slave)
		elif osID.upper() == "LINUX_32":
			cmd_spi_app_read = str(dut_app_loc) + str(dut_app) + " " + \
							   str(dut_spi_port) + " " + str(bytesize) + " " + str(speed) + " " + \
							   str(order) + " " + str(mode) + " " + str(slave)
	 
		print cmd_spi_app_read
		cmd_logging = "echo " + cmd_spi_app_read + " >> " + testlog_loc
		thm.execute(cmd_logging)

		#for android, dut is accessed through thm. Otherwise, need to command to dut directly.
		if osID.upper() == "ANDROID":
			read_app_output = thm.execute(cmd_spi_app_read)
		else:
			read_app_output = dut.execute(cmd_spi_app_read)

		print read_app_output
		cmd_logging = "echo " + read_app_output + " >> " + testlog_loc
		thm.execute(cmd_logging)
		
		#format expected data to be lower case with no spaces
		data = app_data  

		expected_data = string.replace(data, " " , "")
		expected_data = string.lower(expected_data)
		aadvark_data=""
		  
		splitter = re.compile("\n")
		read_list = splitter.split(read_app_output)
			
		try:
			for line in read_list:
				if re.search("data=" ,line):
					parsed = re.search("(?<=data\D)\w+", str(line))
					initial_data = parsed.group(0).lstrip()
					aadvark_data += initial_data
					if len(aadvark_data) == (api_num_bytes * 2):  #check to length of expected data
						break
			   
		except:
			aadvark_data=""

		print "Expected Data: " + expected_data
		cmd_logging = "echo Expected Data: " + expected_data + " >> " + testlog_loc
		thm.execute(cmd_logging)

		print "Read Data: " + aadvark_data
		cmd_logging = "echo Read Data: " + aadvark_data + " >> " + testlog_loc
		thm.execute(cmd_logging)

		time.sleep(3)
		#print aadvark_data == expected_data
		#compare data and set result        
		if aadvark_data == expected_data:
			if testVerdict == True:
				testVerdict = True
			write_result = True
			thm.execute("echo DUT Read 0x0" + str(slave) + " expected=" + expected_data + " aadvark_data=" + aadvark_data + " >> " + testlog_loc)
			
		else:
			testVerdict = False
			thm.execute("echo DATA Received Check Failed on Host Machine, DUT Read 0x0" + str(slave) + " expected=" + expected_data + " aadvark_data=" + aadvark_data + " >> " + testlog_loc)

		return testVerdict


	#DUT Write to Aadvark
	def spi_write(port, bytesize , speed, mode, order, slave, num_bytes, full_data, testVerdict, osID):

		temp_list_splitter = re.split ( ":: ", full_data )

		 #the aadvark API only accepts 8 bit long bytes. Thus, we workaround by using two 8 bit bytes which is read by dut as single 16 bit byte.
		if bytesize == 8:
			forward_data = temp_list_splitter[0]
			reverse_data = temp_list_splitter[1]

			padding_bytes = ""        
			
			api_data = forward_data
			app_data = forward_data

			api_num_bytes = num_bytes

		elif bytesize == 16:
			forward_data = temp_list_splitter[0]
			forward_data_8bit = temp_list_splitter[1] #this is the 16 bit split to 8 bit chunks.
			reverse_data = temp_list_splitter[2]
			
			padding_bytes = "00 00 "

			api_data = padding_bytes + forward_data_8bit #pad the header bytes"
			app_data = forward_data

			api_num_bytes = num_bytes * 2

		elif bytesize == 32:
			forward_data = temp_list_splitter[0]
			forward_data_8bit = temp_list_splitter[1] #this is the 16 bit split to 8 bit chunks.
			reverse_data = temp_list_splitter[2]

			padding_bytes = "00 00 00 00 00 00 "

			api_data = padding_bytes + forward_data_8bit
			app_data = forward_data

			api_num_bytes = num_bytes * 4

		
		cmd_remove_thmlog = "rm " + avk_log
		print cmd_remove_thmlog
		thm.execute(cmd_remove_thmlog)
		print "here"
		#send python command in format "python <python.py> <aadvark_port> <mode> <bitorder> <slave_address_hex> <timeout_ms> <num_bytes> <data>" stdout redirected to log_file and terminal
		cmd_execute_api = "python " + str(avk_api_loc) + str(avk_spislave_script) +  " " + str(port) + \
						 " " + str(mode) + " " + str(order) + " 0x0" + str(slave) + " " + str(avk_timeout) + \
						 " " + str(bytesize) + " " + str(api_num_bytes) + " " + str(api_data) 
		#cmd_execute_api = "python /home/siv_test_collateral/siv_val-io-test-apps/misc/aadvark-api-v5.13/linux-x86_64/python/aaspi_slave.py 0 0 msb 0x050 50000 8 8 "+ data +"  2>&1 | tee /root/spi.log"

		retry_loop_counter = 1

		while retry_loop_counter < 5:
			print "============ Write Cycle Try: " + str(retry_loop_counter) + "=============="

		        print cmd_execute_api
			cmd_logging = "echo " + cmd_execute_api + " >> " + testlog_loc
			thm.execute(cmd_logging)

			thm.timeexecute(cmd_execute_api)

			time.sleep(2)
			#command dut to execute app in format " ./<app> </dev/spidev-port> <bytesize> <speed> <bitorder> <mode> <slave_address> <write_data_bytes>
			if osID.upper() == "ANDROID":
				cmd_spi_app_write = "adb shell ." + str(dut_app_loc) + "android" + str(dut_app) + " " + \
									str(dut_spi_port) + " " + str(bytesize) + " " + str(speed) + " " + str(order) + \
									" " + str(mode) + " " + str(slave) + " " + str(app_data) + "2>&1"
			elif osID.upper() == "LINUX_64":
				cmd_spi_app_write = str(dut_app_loc) + str(dut_app) + " " + \
									str(dut_spi_port) + " " + str(bytesize) + " " + str(speed) + " " + str(order) + \
									" " + str(mode) + " " + str(slave) + " " + str(app_data)
			elif osID.upper() == "LINUX_32":
				cmd_spi_app_write = str(dut_app_loc) + str(dut_app) + " " + \
									str(dut_spi_port) + " " + str(bytesize) + " " + str(speed) + " " + str(order) + \
									" " + str(mode) + " " + str(slave) + " " + str(app_data)+ "2>&1"

			print "APP WRITE:" + cmd_spi_app_write
			cmd_logging = "echo " + cmd_spi_app_write + " >> " + testlog_loc
			thm.execute(cmd_logging)

			#for android, dut is accessed through thm. Otherwise, need to command to dut directly.
			if osID.upper() == "ANDROID":
				thm.execute(cmd_spi_app_write)
			else:
				print "Output: " + dut.execute(cmd_spi_app_write)

			#format expected data to be lower case with no spaces
			data = app_data
			print "Expected data without process : " + data
			expected_data = string.replace(data, " " , "")
			expected_data = string.lower(expected_data)
			aadvark_data=""

			time.sleep(5)

			cmd_cat_thmlog = "cat " + avk_log
			print cmd_cat_thmlog
			cmd_logging = "echo " + cmd_cat_thmlog + " >> " + testlog_loc
			thm.execute(cmd_logging) 

			result = thm.execute(cmd_cat_thmlog)

			print "Result: " + result
			#split to list based on splitter "newline"
			splitter = re.compile("\n")
			write_list = splitter.split(result)
			if bitlength <= 8:
				write_list = write_list[5:]
			else:
				write_list = write_list[16:]
			search_header = "02"
			search_address = str(slave)
			
			if order == 'lsb':
				search_header = common.reverse_binary(02)
				search_address = "ff"
			print write_list
			try:
				for line in write_list:
					initial_data= line.replace(' ', '')
					aadvark_data += initial_data
				# 	if re.search("0000:" ,line) and re.search(str(search_header) ,line):
				# 		initial_data= line.replace(' ', '')
				#                 padding_data = padding_bytes.replace(' ', '')
				# 		print "LINE " + line
				# 		parsed = re.search("(?<=" + str(search_header) + str(padding_data) + str(search_address) + ")\w+", str(initial_data))
				# 		aadvark_data = parsed.group(0).lstrip()
				# 
				# 	elif re.search("0010:" ,line) :
				# 		initial_data= line.replace(' ', '')
				# 		print "LINE " + line
				# 		parsed = re.search("(?<=0010:)\w+", str(initial_data))
				# 		aadvark_data += parsed.group(0).lstrip()
				# 
				# 	elif re.search("0020:" ,line) :
				# 		initial_data= line.replace(' ', '')
				# 		print "LINE " + line
				# 		parsed = re.search("(?<=0020:)\w+", str(initial_data))
				# 		aadvark_data += parsed.group(0).lstrip()
				# 
				# 	elif re.search("0030:" ,line) :
				# 		initial_data= line.replace(' ', '')
				# 		print "LINE " + line
				# 		parsed = re.search("(?<=0020:)\w+", str(initial_data))
				# 		aadvark_data += parsed.group(0).lstrip()
			except:
				aadvark_data=""
			
			print "AARDVARK DATA : " + aadvark_data
			if aadvark_data == "":
				print "No Aardvark Data due to time out of device. Retrying Write Cycle Try:" + str(retry_loop_counter)
				retry_loop_counter = retry_loop_counter + 1
			else:
				thm.execute("echo Aardvard Written data found " + result + " >> " + testlog_loc)
				thm.execute("echo Aardvard Written data parsed " + aadvark_data + " >> " + testlog_loc)
				print "Exit Write Loop. Aardvark Data Found:"
				break
				
				

		print "Expected Data: " + expected_data
		cmd_logging = "echo Expected Data: " + expected_data + " >> " + testlog_loc
		thm.execute(cmd_logging)

		print "Write Data: " + aadvark_data
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

		print cmd_remove_thmlog
		cmd_logging = "echo " + cmd_remove_thmlog + " >> " + testlog_loc
		thm.execute(cmd_logging)

		#thm.execute(cmd_remove_thmlog)
		
		return testVerdict


	#Auto Loop Functions

	def data_byte_loop (speed, mode, bitorder, bitlength):
		curr_speed = speed
		curr_mode = mode
		curr_bitorder = bitorder
		curr_bitlength = bitlength
		curr_bytes = min_bytes
		curr_loop_verdict = True
		
		testVerdict = True

		try:
			while curr_bytes <= max_bytes:
				internal_loop_verdict = False
				
				#Actual test starts here

				data = common.gen_random_hex(int(curr_bytes), int(curr_bitlength))
				internal_loop_verdict =  spi_read(aadvark_usb_port, curr_bitlength, curr_speed, curr_mode, curr_bitorder, 50, int(curr_bytes) , data, testVerdict, osID)

				if internal_loop_verdict == True:
					  internal_loop_verdict_out= "Pass"
				else:
					  internal_loop_verdict_out= "Fail"                 

				thm.execute("echo [SPI_RESULT]Speed: " + str(curr_speed) + " kbits, Mode: " + str(curr_mode) + " , Bitorder: " + str(curr_bitorder) + \
						   " , Bitlength: " + str(bitlength) + " , Read Data: " + str(curr_bytes) + " -- " + str(internal_loop_verdict_out) + " >> " + testlog_loc)
				print "    Speed: " + str(curr_speed) + " kbits, Mode: " + str(curr_mode) + " , Bitorder: " + str(curr_bitorder) + \
						   " , Bitlength: " + str(bitlength) + " , Read Data: " + str(curr_bytes) + " -- " + str(internal_loop_verdict_out)

				curr_loop_verdict = curr_loop_verdict and internal_loop_verdict

				internal_loop_verdict = False

				data = common.gen_random_hex(int(curr_bytes),  int(curr_bitlength))
				#data = "AA CC DD EE AC AE DE ED :: AA BB CC 11 22 33 91 92"
				internal_loop_verdict = spi_write(aadvark_usb_port, curr_bitlength, curr_speed, curr_mode, curr_bitorder, 50, int(curr_bytes) , data, testVerdict, osID)

				if internal_loop_verdict == True:
					  internal_loop_verdict_out= "Pass"
				else:
					  internal_loop_verdict_out= "Fail"                 

				thm.execute("echo [SPI_RESULT]Speed: " + str(curr_speed) + " kbits, Mode: " + str(curr_mode) + " , Bitorder: " + str(curr_bitorder) + \
						   " , Bitlength: " + str(bitlength) + " , Write Data: " + str(curr_bytes) + " -- " + str(internal_loop_verdict_out) + " >> " + testlog_loc)
				print "    Speed: " + str(curr_speed) + " kbits, Mode: " + str(curr_mode) + " , Bitorder: " + str(curr_bitorder) + \
						   " , Bitlength: " + str(bitlength) + " , Write Data: " + str(curr_bytes) + " -- " + str(internal_loop_verdict_out)

				curr_loop_verdict = curr_loop_verdict and internal_loop_verdict

				#Actual test ends here

				curr_bytes = curr_bytes + 1

			return curr_loop_verdict

		except StandardError, e:
			thm.execute("echo ERROR: Terminated in Data Loop " + str(e) + " >> " + testlog_loc)
			print "ERROR: Terminated in Data Loop" + str(e)
			sys.exit(1)

	def bitlength_loop (speed, mode, bitorder):
		curr_speed = speed
		curr_mode = mode
		curr_bitorder = bitorder
		curr_bitlength = min_bitlength_index
		curr_loop_verdict = True
		try:
			while curr_bitlength <= max_bitlength_index:
				internal_loop_verdict = True
				
				#Actual test starts here
				bitlength = bitlength_lookup(curr_bitlength)

				internal_loop_verdict = data_byte_loop (curr_speed, curr_mode, curr_bitorder, bitlength)

				curr_loop_verdict = curr_loop_verdict and internal_loop_verdict

				#Actual test ends here

				if internal_loop_verdict == True:
					  internal_loop_verdict_out= "Pass"
				else:
					  internal_loop_verdict_out= "Fail"                 

				curr_bitlength = curr_bitlength + 1

			return curr_loop_verdict

		except StandardError, e:
			thm.execute("echo ERROR: Terminated in Bitlength Loop " + str(e) + " >> " + testlog_loc)
			print "ERROR: Terminated in Bitlength Loop" + str(e)
			sys.exit(1)

	def bitorder_loop (speed, mode):
		curr_speed = speed
		curr_mode = mode
		curr_bitorder=min_bitorder_index
		curr_loop_verdict=True
		try:
			while curr_bitorder <= max_bitorder_index:
				internal_loop_verdict = True
				
				#Actual test starts here
				bitorder = bitorder_lookup(curr_bitorder)

				internal_loop_verdict = bitlength_loop (curr_speed, curr_mode, bitorder)

				curr_loop_verdict = curr_loop_verdict and internal_loop_verdict

				#Actual test ends here

				if internal_loop_verdict == True:
					  internal_loop_verdict_out= "Pass"
				else:
					  internal_loop_verdict_out= "Fail"                 

				curr_bitorder=curr_bitorder + 1

			return curr_loop_verdict

		except StandardError, e:
			thm.execute("echo ERROR: Terminated in Bitorder Loop " + str(e) + " >> " + testlog_loc)
			print "ERROR: Terminated in Bitorder Loop" + str(e)
			sys.exit(1)


	def mode_loop (speed):
		curr_speed = speed
		curr_mode = min_mode
		curr_loop_verdict = True
		try:
			while curr_mode <= max_mode:
				internal_loop_verdict = True
				
				#Actual test starts here

				internal_loop_verdict = bitorder_loop (curr_speed, curr_mode)

				curr_loop_verdict = curr_loop_verdict and internal_loop_verdict

				#Actual test ends here

				if internal_loop_verdict == True:
					  internal_loop_verdict_out= "Pass"
				else:
					  internal_loop_verdict_out= "Fail"                 

				curr_mode=curr_mode + 1

			return curr_loop_verdict

		except StandardError, e:
			thm.execute("echo ERROR: Terminated in Mode Loop " + str(e) + " >> " + testlog_loc)
			print "ERROR: Terminated in Mode Loop" + str(e)
			sys.exit(1)

	def speed_loop_main ():
		overall_verdict = True
		test_result = True
		curr_speed = min_speed_index
		
		try:
			while curr_speed <= max_speed_index:
				thm.execute("echo [SPI_RESULT]======================================= " + " >> " + testlog_loc)
				print "======================================="

				curr_mode = min_mode
				curr_loop_verdict = True

				speed = speed_lookup(curr_speed)

				curr_loop_verdict = mode_loop(speed)
				overall_verdict = overall_verdict and curr_loop_verdict 

				thm.execute("echo [SPI_RESULT]======================================= " + " >> " + testlog_loc)
				print "======================================="

				if curr_loop_verdict == True:
					  curr_loop_verdict_out = "PASSED"
				else:
					  curr_loop_verdict_out = "FAILED"       

				thm.execute("echo [SPI_RESULT]Speed Test: " + str(speed) + " -- " + str(curr_loop_verdict_out) + " >> " + testlog_loc)      
				print "Speeed Test: " + str(speed) + " kbits -- " + str(curr_loop_verdict_out)

				curr_speed = curr_speed + 1            

			thm.execute("echo [SPI_RESULT]======================================= " + " >> " + testlog_loc)
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

		except StandardError, e:
			thm.execute("echo ERROR: Terminated in Speed Loop " + str(e) + " >> " + testlog_loc)
			print "echo ERROR: Terminated in Speed Loop" + str(e)
			sys.exit(1)


	#Start of Main Script

	### Get Argument ####

	#try:
	#    opts, args = getopt.getopt(sys.argv[1:], 't:r:o:m:b:c:l:e:a:s:d:z:f:')
	#    for opt, arg in opts:
	#        if opt == '-t':
	#            testID = str(arg)
	#        elif opt == '-r':
	#            projectID = str(arg)
	#        elif opt == '-o':
	#            osID = str(arg)
	#        elif opt == '-m':
	#            read_write_mode = str(arg)
	#        elif opt == '-b':
	#            num_bytes = int(arg)
	#       elif opt == '-c':
	#           bitorder = str(arg)
	#        elif opt == '-l':
	#            bitlength = int(arg)
	#        elif opt == '-e':
	#            mode = int(arg)
	#        elif opt == '-a':
	#            slave_address = str(arg)
	#        elif opt == '-s':
	#            speed = str(arg)
	#        elif opt == '-d':
	#            dma = str(arg)
	#       elif opt == '-z':
	#            suite = str(arg)
	#       elif opt == '-f':
	#            dut_num = int(arg)                  
	#except StandardError , e:
	#        print e

	#currentDate = common.get_date()  # get today's date
	#Time_now = common.get_current_time() # get current time
	#date_time = currentDate + "_" + Time_now  #form timestamp

	#log_dir = testlog_dir + str(currentDate) + "_"+ str(dut_num) +"/"

	#testlog_loc = testlog_dir + str(testID) + "_" + str(date_time) + "_" + str(dut_num) + ".log"    

	if avk_api_loc == "":
		avk_api_loc = "/root/aardvark-api-linux-i686-v5.13"

	test_result = True

	#This switch is to enable multiple DUT to be tested with a single THM.
	#use aadetect.py in /test-apps/misc/aadvark-api-v5.13/linux_x86/python
	if dut_num == 1:
		dut_ip = dut_ip1
		aadvark_usb_port = aadvark_usb_port1
	elif dut_num == 2:
		dut_ip = dut_ip2
		aadvark_usb_port = aadvark_usb_port2
	else:
		sys.exit(1)

	print "DUT IP Used :" + str(dut_ip)
	print "Aadvark USB Port Used :" + str(aadvark_usb_port)

		
	try:
		# if osID.upper() == "ANDROID":
			# thm = GenericCommand.GenericCommand()
			# thm.login(thm_ip)

			# thm.execute("adb devices")
			
			# thm.execute("mkdir -p " + testlog_dir)

		# else:
			# thm = GenericCommand.GenericCommand()
			# thm.login(thm_ip)
		 
			# thm.execute("mkdir -p " + testlog_dir)

			# dut = GenericCommand.GenericCommand()
			# dut.login(dut_ip)

		if suite.lower() == "auto":
			speed_loop_main()

		else:

			print "Read/Write Mode: " + read_write_mode 
			thm.execute("echo Read/Write Mode: " + read_write_mode + " >> " + testlog_loc)

			print "Num Bytes: " + str(num_bytes) 
			thm.execute("echo Read/Write Mode: " + str(num_bytes) + " >> " + testlog_loc)
			data = ""
			data = common.gen_random_hex(int(num_bytes), int(bitlength))
			#data = "AA CC DD EE AC AE DE ED :: AA BB CC 11 22 33 91 92"
			print "Data: " + data
			thm.execute("echo Data     : " + data + " >> " + testlog_loc)

			print "Bit Order: " + bitorder
			thm.execute("echo Bit Ordering: " + bitorder + " >> " + testlog_loc)

			print "SPI Mode: " + str(mode) 
			thm.execute("echo SPI Mode: " + str(mode) + " >> " + testlog_loc)

			print "Slave Address: " + str(slave_address)
			thm.execute("echo Slave Address: " + str(slave_address) + " >> " + testlog_loc)

			print "Speed: " + str(speed)
			thm.execute("echo Speed: " + str(speed) + " >> " + testlog_loc)

			print "DMA: " + dma
			thm.execute("echo DMA: " + dma + " >> " + testlog_loc)

			print "Suite/Negative Test: " + suite
			thm.execute("echo Suite/Negative Test: " + suite + " >> " + testlog_loc)

			#negative_test = False
				
			#if suite == "negative":
			#	negative_test = True
			
			testVerdict = True
			test_result = False

			if read_write_mode.upper() == "READ":   
				test_result = spi_read(aadvark_usb_port, bitlength, speed, mode, bitorder, slave_address, int(num_bytes) , data, testVerdict, osID)

			elif read_write_mode.upper() == "WRITE":
				test_result = spi_write(aadvark_usb_port, bitlength, speed, mode, bitorder, slave_address, int(num_bytes) , data, testVerdict, osID)
			else:
				test_result = False

			#For True Tests Return the actual result
			if negative_test == False:
				if test_result == True: 
					print "VERDICT: SPI Test Pass!!"
					thm.execute("echo SPI Test Pass!! >> " + testlog_loc)
					sys.exit(0)
				else:
					print "VERDICT: SPI Test Fail!!"
					thm.execute("echo SPI Test Fail!! >> " + testlog_loc)
					sys.exit(1)
			#For Negative Tests (False Negatives) return an invert of the result.
			elif negative_test == True:
				if test_result == True: 
					print "VERDICT: SPI Test Fail!!"
					thm.execute("echo SPI Negative Test Fail!! Supposed to Fail >> " + testlog_loc)
					sys.exit(1)
				else:
					print "VERDICT: SPI Test Pass!!"
					thm.execute("echo SPI Negative Test Pass!! Expected to Fail.>> " + testlog_loc)
					sys.exit(0)

	except StandardError, e:
		thm.execute("echo TEST ERROR " + str(e) + " >> " + testlog_loc)
		test_result = False
		sys.exit(1)
		
if tool == "EEPROM":
                ##For High Speed SPI executions
                print "Running High Speed SPI Test"

                result = dut.execute("bash /home/siv_test_collateral/siv_val-io-test-apps/spi/spiEEPROM_script " + dut_spi_port + " " + str(speed) + " " + str(mode) + " "+str(num_bytes))
                verdict = str(dut.execute("echo $?"))

                print result
                
                if not os.path.exists(testlog_dir):
                    os.makedirs(testlog_dir)
                with open(testlog_loc,"w") as log:
                    log.write(result)
                    log.close()

                if result.find('PASS') is -1:

                    count = 1
                    while (count < 3):
                        print "Retest " + str(count)
                        result = dut.execute("bash /home/siv_test_collateral/siv_val-io-test-apps/spi/spiEEPROM_script " + dut_spi_port + " " + str(speed) + " " + str(mode) + " "+str(num_bytes))
                        verdict = str(dut.execute("echo $?"))
                        print result
                        with open(testlog_loc,"a") as log: #Write to log
                            log.write(result)
                            log.close()
                        if verdict == "0":
                            if negative_test:
                                print "[DEBUG] Negative test on"
                                print "VERDICT: SPI Test Fail!!"
                                sys.exit(1)
                            else:
                                print "VERDICT: SPI Test Pass!!"
                                sys.exit(0)

                        count = count + 1
                    if count >= 3:
                        if negative_test:
                            print "[DEBUG] Negative test on"
                            print "VERDICT: SPI Test Pass!!"
                            sys.exit(0)
                        else:
                            print "VERDICT: SPI Test Fail!!"
                            sys.exit(1)

                else:
                    if negative_test:
                        print "[DEBUG] Negative test on"
                        print "VERDICT: SPI Test Fail!!"
                        sys.exit(1)
                    else:
                        print "[DEBUG] Negative test off"
                        print "VERDICT: SPI Test Pass!!"
                        sys.exit(0)
