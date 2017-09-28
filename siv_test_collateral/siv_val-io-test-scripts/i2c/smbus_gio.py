import sys, os, re, time, argparse, GenericCommand, string, common, random
from datetime import date, datetime

#Default parameters
gcs_port = "2300"

script_name = str(sys.argv[0])
usage = "This is smbus test"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-ip', help='SUT IP')
parser.add_argument('-pf', help='Platform')
parser.add_argument('-op', help='Operation [rw]')
parser.add_argument('-smbus_address', help='0x4c')
parser.add_argument('-read_op_address', help='0x4c')
parser.add_argument('-write_op_address', help='0x4c')
parser.add_argument('-dump_data', help='0x4c')
args = parser.parse_args()

if args.ip is not None:
    dev_1_ip = args.ip
    
if args.pf is not None:
    platform = args.pf.upper()

if args.op is not None:
    operation = args.op

if args.smbus_address is not None:
    smbus_address = args.smbus_address
else:
	print "smbus address missing"
	sys.exit(1)

if args.read_op_address is not None:
    read_operation = args.read_op_address
else:
	print "read address missing"
	sys.exit(1)

if args.write_op_address is not None:
    write_operation = args.write_op_address
else:
	print "write address missing"
	sys.exit(1)

if args.dump_data is not None:
    dump_data = args.dump_data
else:
	print "dump data missing"
	sys.exit(1)

dut = GenericCommand.GenericCommand()
dut.login(dev_1_ip, gcs_port)

splitter_dash = re.compile("-")
splitter_next = re.compile("\n")
ldata = str(dut.execute("i2cdetect -l | grep -i 'SMBus I801 adapter' | grep -v part | awk '{split($1,a); print a[1]}'"))
driver_num = splitter_next.split(splitter_dash.split(ldata)[1])[0]

if platform == "BXT":
	# smbus_address = "0x4c"
	# read_operation = "0x04"
	# write_operation = "0x0A"
	# dump_data = "0x06"
	additional_parameter = ""
elif platform == "BYT":
	# smbus_address = "0x50"
	# read_operation = "0xc0"
	# write_operation = "0xc0"
	# dump_data = "0x06"
	additional_parameter = "c"

def smbus_read_write():
	print "====SMBus Read Write Test===="
	before_value = dut.execute("i2cget -y" + " " + driver_num + " " + smbus_address + " " + read_operation)
	dut.execute("i2cset -y" + " " + driver_num + " " + smbus_address + " " + write_operation + " " + dump_data)
	edited_value = dut.execute("i2cget -y" + " " + driver_num + " " + smbus_address + " " + read_operation)
	print "Original Value: " + before_value + "\nEdited Value: " + edited_value + "\n"
	
	if before_value != edited_value:
		print "SMBUS Read Write Test: PASS"
		sys.exit(0)
	else:
		print "SMBUS Read Write Test: FAIL"
		sys.exit(1)

def smbus_port_driver_capability_verification():
	print "====SMBus Port and Driver Capability Test===="
	print "i2cdump -y" + " " + driver_num + " " + smbus_address + " " + additional_parameter
	smbus_i2c_dump_data = dut.execute("i2cdump -y" + " " + driver_num + " " + smbus_address + " " + additional_parameter)
	print "I2C Dump Data: \n" +smbus_i2c_dump_data
	if "XX XX XX XX XX" not in smbus_i2c_dump_data :
		print "I2C Tool and SMBus Capability PASS"
		sys.exit(0)
	else:
		print "I2C Tool and SMBus Capability FAIL"
		sys.exit(1)

def list_node():
    print "====SMBus List Node Test===="
    dut.execute("rm -rf /*.log")
    dut.execute("ls -l /dev/i2c-* | grep -v part| awk '{split($10,a); print a[1]}' >> /ls_data.log")
    dut.execute("i2cdetect -l | grep -v part | awk '{split($1,a); print a[1]}' >> /tool_data.log")
    if dut.execute("diff /ls_data.log /tool_data.log"):
        print "List Node Test PASS"
        sys.exit(0)
    else:
        print "List Node Test FAIL"
        sys.exit(1)

def master_mode():
    print "====SMBus Master Mode Test===="
    smbus_i2c_dump_data = dut.execute("i2cdump -y" + " " + driver_num + " " + smbus_address)
    if dut.execute("i2cget -y" + " " + driver_num + " " + smbus_address + " 0") != "00":
        print "SMBus Master Mode Test PASS"
        sys.exit(0)
    else:
        print "SMBus Master Mode Test FAIL"
        sys.exit(1)


def main():
    if operation == "rw":
        smbus_read_write() # Test case : SMB-F004-M
    elif operation == "pdcv":
        smbus_port_driver_capability_verification() # Test case : SMB-F007-M
    elif operation == "lsn":
        list_node() # Test Case : SMB-F008-M
    elif operation == "master":
        master_mode() # Test Case: SMB_F009-M
        
        
main()