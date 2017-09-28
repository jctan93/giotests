import os, sys, json, subprocess, re, time, datetime, multiprocessing, argparse, glob, os.path
from ssh_util import *

file_location = "/home/ped-bxt-release-proprietary-local/"
ipu_rpm_location = "/home/latest_ipu_rpms/"
# ipu_component_list = ['ipu4fw', 'icamera', 'aiqb', 'libcamhal', 'libiaaiq', 'libiacss']
operation_list = ["chk_package_gcc", "chk_package_availability", "chk_kernel_version", "chk_package_installation", "chk_runlevel", "chk_poky_version",
				  "chk_architecture"]
compress_fileformat_list = ["tar.bz2", "tar.gz", "zip"]
flag_verdict = []

script_name = str(sys.argv[0])
usage = "This is yocto detail test"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-thm_ip', help='THM IP')
parser.add_argument('-op', help='Operation = [chk_package_gcc, chk_package_availability, chk_kernel_version, chk_package_installation, chk_runlevel, chk_poky_version, chk_architecture]')
parser.add_argument('-key', help='Input parameter a.k.a keyword')
parser.add_argument('-ver', help='Input version', default = "")
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip
if args.thm_ip is not None:
	thm_ip = args.thm_ip
if args.op is not None:
	operation = args.op
	if operation in operation_list:
		if args.key is not None:
			keyword = args.key
		if args.ver is not None:
			version = args.ver
		else:
			print "either -key or -ver is empty."
			sys.exit(1)

ssh_sut = ssh_com(sut_ip)
ssh_sut.setpub(sshpass="")
ssh_thm = ssh_com(thm_ip)
ssh_thm.setpub(sshpass="bxtroot")

splitter_comma = re.compile(",")
splitter_dash = re.compile("-")
splitter_rpmext = re.compile(".rpm")
splitter_next = re.compile("\n")
splitter_space = re.compile(" ")
splitter_gnu = re.compile('(GNU)')
splitter_equal = re.compile("=")
splitter_doublequote = re.compile('"')

def check_package_availability():
	if version == "":
		print "Version number missing"
		sys.exit(1)
	output_result = ssh_sut.ssh_exec("rpm -q " + keyword + " --queryformat '%{NAME}'")
	if keyword in output_result:
		output_version = ssh_sut.ssh_exec("rpm -q " + output_result + " --queryformat '%{VERSION}'")
		print "\n\n======= Check Package Availability Result ==========\n"
		print "Search package : " + keyword + "\nPackage found : " + output_result +"\nInput Version : " + version + "\nPackage Version : " + output_version
		print "\n===================================================="
		
		if (keyword == output_result)| (version <= output_version):
			flag_verdict.append("True")
		else:
			flag_verdict.append("False")
			
	if (flag_verdict[1:] == flag_verdict[:-1]) and ("True" in flag_verdict[:]):
		verdict = True
	else:
		verdict = False
	return verdict

def check_package_gcc():
	if version == "":
		print "GCC Version number missing"
		sys.exit(1)
	ssh_thm.ssh_exec("scp -r root@"+ sut_ip + ":" + file_location + "* " + ipu_rpm_location )
	ssh_thm.ssh_exec("cd " + ipu_rpm_location + ";mv " + ipu_rpm_location + "GPA/* .; mv " + ipu_rpm_location + "gstreamer/* .; mv " + ipu_rpm_location + "MediaSDK/* .; mv " + ipu_rpm_location + "UFO/* .; mv " + ipu_rpm_location + "Weston/* .")
	file_all_list = ssh_thm.ssh_exec("ls " + ipu_rpm_location)
	file_all_list_with_keyword = ssh_thm.ssh_exec("ls " + ipu_rpm_location + " | grep " + keyword)
	print file_all_list_with_keyword
	print "tar --strip-components=1 -xf "+ ipu_rpm_location + file_all_list_with_keyword
	if keyword in file_all_list:
		if ".rpm" in file_all_list_with_keyword:
			rpm_file = splitter_next.split(ssh_sut.ssh_exec("rpm -q " + keyword))[-2]
			ssh_thm.ssh_exec("mkdir " + ipu_rpm_location + keyword + "; cd "+ ipu_rpm_location + keyword + "; rpm2cpio ../"+ rpm_file + ".rpm | cpio -idmv")
		elif ".tar.gz" or ".tar.bz2" in file_all_list_with_keyword:
			ssh_thm.ssh_exec("mkdir " + ipu_rpm_location + keyword + "; tar --strip-components=1 -xf "+ ipu_rpm_location + splitter_next.split(file_all_list_with_keyword)[0] + " -C " + ipu_rpm_location + keyword)
		elif ".zip" in file_all_list_with_keyword:
			ssh_thm.ssh_exec("mkdir " + ipu_rpm_location + keyword + "; unzip "+ ipu_rpm_location + splitter_next.split(file_all_list_with_keyword)[0] + " -d " + ipu_rpm_location + keyword)
		for dirpath, dirnames, filenames in os.walk(ipu_rpm_location + keyword):
			for filename in [f for f in filenames ]:
				if "Not an ELF file" in ssh_thm.ssh_exec("readelf -p .comment "+ os.path.join(dirpath, filename)):
					continue
				if splitter_next.split(splitter_space.split(splitter_gnu.split(ssh_thm.ssh_exec("readelf -p .comment "+ os.path.join(dirpath, filename)))[-1])[-1])[0] >= version:
					flag_verdict.append("True")
				else:
					flag_verdict.append("False")
	if (flag_verdict[1:] == flag_verdict[:-1]) and ("True" in flag_verdict[:]):
		verdict = True
	else:
		verdict = False
	return verdict
		
def check_kernel_version():
	kernel_version = splitter_dash.split(ssh_sut.ssh_exec("uname -r"))[0]
	print "\n\n============= Check Kernel Version Result =================\n"
	print "Input Kernel Version : " + keyword + "\nOutput Kernel Version from system : " + kernel_version
	print "\n==========================================================="
	if keyword <= kernel_version:
		verdict  = True
	else:
		print "Kernel version is less than " + keyword
		verdict  = False
	return verdict

def check_package_installation():
	installed_rpm = ssh_sut.ssh_exec("rpm -q " + keyword)
	if "not installed" not in installed_rpm:
		print installed_rpm + " installed successfully"
		verdict = True
		# if keyword not in ipu_component_list:
		# 	if ssh_sut.ssh_exec("dmesg | grep mismatch | grep intel_ipu4") != "":
		# 		verdict = True
		# 	else:
		# 		verdict = False
		# elif keyword == "kernel-module-hid-sensor-iio-common":
		# 	if ssh_sut.ssh_exec("ls /dev/ | grep iio") != "":
		# 		verdict = True
		# 	else:
		# 		verdict = False
	else:
		print keyword + " not installed successfully"
		verdict = False
	return verdict

def check_runlevel():
	current_output = splitter_space.split(ssh_sut.ssh_exec("runlevel"))[1]
	print "Current output : " + current_output
	print "Expected output : " + keyword
	if keyword == current_output:
		print "Runlevel matched"
		verdict = True
	else:
		print "Runlevel mismatch"
		verdict = False
	return verdict

def check_poky_version():
	output_poky_version = splitter_doublequote.split(splitter_equal.split(ssh_sut.ssh_exec("cat /etc/os-release | grep -i version_id"))[1])[1]
	print "\n\n============= Check Poky Version Result =================\n"
	print "Input Poky Version : " + version + "\nOutput Poky Version from system : " + output_poky_version
	print "\n==========================================================="
	if version <= output_poky_version:
		verdict  = True
	else:
		print "Poky version is less than " + version
		verdict  = False
	return verdict

def check_architecture():
	output_architecture = splitter_next.split(ssh_sut.ssh_exec("uname -m"))[0]
	print "\n\n============= Check OS Architecture Result =================\n"
	print "Input OS Architecture : " + keyword + "\nOutput OS Architecture from system : " + output_architecture
	print "\n==========================================================="
	if keyword == output_architecture:
		verdict  = True
	else:
		print "OS Architecture is not " + keyword
		verdict  = False
	return verdict

def main():
	if operation == "chk_package_gcc":
		verdict = check_package_gcc()
	elif operation == "chk_package_availability":
		verdict = check_package_availability()
	elif operation == "chk_kernel_version":
		verdict = check_kernel_version()
	elif operation == "chk_package_installation":
		verdict = check_package_installation()
	elif operation == "chk_runlevel":
		verdict = check_runlevel()
	elif operation == "chk_poky_version":
		verdict = check_poky_version()
	elif operation == "chk_architecture":
		verdict = check_architecture()
	if verdict:
		print "\nFinal Test Verdict : PASS"
		sys.exit(0)
	else:
		print "\nFinal Test Verdict : FAIL"
		sys.exit(1)
		
main()