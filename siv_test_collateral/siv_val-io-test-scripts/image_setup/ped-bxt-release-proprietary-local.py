#!/usr/bin/python

import os, sys, json, netrc, base64, httplib2, subprocess, re, time, datetime, multiprocessing, argparse, glob
from ssh_util import *

file_location = "/home/ped-bxt-release-proprietary-local/"
required_rpm_list = ['VPG_Media_UFO', 'gstreamer_MSDK_plugin', 'IAS', 'MediaSDK', 'GPA']
data_list_gpa = []
data_list_ufo = []
data_list_gstreamer = []
data_list_ias = []
data_list_msdk = []
uninstall_rpm_list = []

splitter_comma = re.compile(",")
splitter_rpmext = re.compile(".rpm")

script_name = str(sys.argv[0])
usage = "Purpose: Downloading UFO, IAS, MSDK and etc from Artifactory and Install those RPM"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-thm_ip', help='THM IP')
parser.add_argument('-op', help='Operation = [pull, install]')
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip
if args.thm_ip is not None:
	thm_ip = args.thm_ip
else: thm_ip = "172.30.248.12"
if args.op is not None:
	operation = args.op

ssh_dut = ssh_com(sut_ip)
ssh_dut.setpub(sshpass="")
ssh_thm = ssh_com(thm_ip)
ssh_thm.setpub(sshpass="bxtroot")

def pull_rpm():
	splitter_fslash = re.compile("/")
	# cur_dir = os.path.dirname(os.path.abspath(__file__))
	cur_dir = os.path.dirname("/home/")
	netrc_lookup = netrc.netrc()
	machine = netrc_lookup.hosts["ubit-artifactory-ba.intel.com"]
	login = machine[0]
	password = machine[2]
	RepoUrl = "ubit-artifactory-ba.intel.com"
	apiPath = "/artifactory/api/search/aql"
	Uri = os.path.join(RepoUrl,apiPath)
	content = """items.find({
			"$and":[
					{"repo":{"$eq":"ped-bxt-release-proprietary-local"}}
			]})"""

	#httplib2.debuglevel = 1
	RepoUrl = "https://ubit-artifactory-ba.intel.com/artifactory/"
	apiPath = "api/search/aql"
	Uri = os.path.join(RepoUrl,apiPath)
	h = httplib2.Http(disable_ssl_certificate_validation=True)
	auth = base64.encodestring( login + ':' + password )
	resp, content = h.request(Uri,'POST',headers = { 'Authorization' : 'Basic ' + auth},body = content)
	print content
	#convert string content to json
	content = json.loads(content)
	if resp["status"] == "200":
		# print resp
		#result_list = content["results"]
		for result in sorted(content["results"]):
			if isinstance(result,dict):
				Created = result["created"]
				Repo = result["repo"]
				Path = result["path"]
				File = result["name"]

			if splitter_fslash.split(Path)[0] == required_rpm_list[0]:
				FileDl = os.path.join(RepoUrl,Repo,Path,File)
				if "intel-linux-ufo-yocto_bxt" in FileDl :
					data_list_ufo.append(FileDl)
			elif splitter_fslash.split(Path)[0] == required_rpm_list[1]:
				FileDl = os.path.join(RepoUrl,Repo,Path,File)
				data_list_gstreamer.append(FileDl)
			elif splitter_fslash.split(Path)[0] == required_rpm_list[2]:
				FileDl = os.path.join(RepoUrl,Repo,Path,File)
				data_list_ias.append(FileDl)
			elif splitter_fslash.split(Path)[0] == required_rpm_list[3]:
				FileDl = os.path.join(RepoUrl,Repo,Path,File)
				data_list_msdk.append(FileDl)
			elif splitter_fslash.split(Path)[0] == required_rpm_list[4]:
				FileDl = os.path.join(RepoUrl,Repo,Path,File)
				if "yocto" in FileDl:
					data_list_gpa.append(FileDl)

		FilePrefix = os.path.join(cur_dir, Repo)
		FileAbsPath = os.path.join(FilePrefix,File)
		os.system("rm -rf " + file_location)
		print "Downloading UFO File from Link : " + data_list_ufo[-1]
		status = os.system("wget --quiet --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + data_list_ufo[-1])
		print "Downloading File from Link : " + data_list_gstreamer[-1]
		status = os.system("wget --quiet --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + data_list_gstreamer[-1])
		print "Downloading File from Link : " + data_list_msdk[-1]
		status = os.system("wget --quiet --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + data_list_msdk[-1])
		print "Downloading File from Link : " + data_list_gpa[-2]
		status = os.system("wget --quiet --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + data_list_gpa[-2])
		for i in data_list_ias[-7:]:
			print "Downloading file from : " + i
			status = os.system("wget --quiet --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + i)

	else:
		print "Error response status --> " + resp["status"]     
		print resp
		return False
	
	return True

def copy_rpms():
	status = os.system("scp -r /home/ped-bxt-release-proprietary-local/. root@" + sut_ip + ":/home/ped-bxt-release-proprietary-local/")
	if status != 0:
		print "Failed to copy to SUT. "
		sys.exit(1)
	else:
		print "Successful transfer rpms"
		
def reverse_copy():
	print "reverse copy"
	print ssh_thm.ssh_exec("scp -r root@" + sut_ip + ":/home/ped-bxt-release-proprietary-local/* /home/latest_ipu_rpms/")

def install_rpms():	
	# install Intel Unified 3D
	ssh_dut.ssh_exec("mkdir " + file_location + "UFO")	
	print "Extracting and install Intel UFO with 3D"
	ssh_dut.ssh_exec("tar xvf "+ file_location +"intel-linux-ufo-yocto_bxt-*.tar.gz -C " + file_location + "UFO")
	ssh_dut.ssh_exec("rpm -ivh " + file_location + "UFO/*.rpm")
	# installed_rpm_list = ssh_dut.ssh_exec("rpm -qa")
	# for i in splitter_comma.split(ssh_dut.ssh_exec("ls " + file_location + "UFO | grep -i rpm" )):
	# 	rpm_package = splitter_rpmext.split(i)[0]
	# 	print rpm_package in installed_rpm_list	
	# 	if rpm_package in installed_rpm_list:
	# 		print rpm_package + " available"
	# 	else:
	# 		print rpm_package + " not available"
	# 		return False
	
	# Install MediaSDK RPM
	ssh_dut.ssh_exec("mkdir " + file_location + "MediaSDK")
	ssh_dut.ssh_exec("tar xvf " + file_location + "IntelMediaSDK*.tar.gz --strip 1 -C " + file_location + "MediaSDK")
	ssh_dut.ssh_exec("rpm -ivh --noparentdirs --nolinktos " + file_location + "MediaSDK/*.rpm")
	# installed_rpm_list = ssh_dut.ssh_exec("rpm -qa")
	# for i in splitter_comma.split(ssh_dut.ssh_exec("ls " + file_location + "MediaSDK | grep -i rpm" )):
	# 	rpm_package = splitter_rpmext.split(i)[0]
	# 	if rpm_package in installed_rpm_list:
	# 		print rpm_package + " available"
	# 	else:
	# 		print rpm_package + " not available"
	# 		return False
	
	# Install gstreamer-mediasdk
	ssh_dut.ssh_exec("mkdir " + file_location + "gstreamer")
	ssh_dut.ssh_exec("tar xvf " + file_location + "gstreamer-mediasdk*.tar.gz --strip 1 -C " + file_location + "gstreamer")
	ssh_dut.ssh_exec("mkdir -p " + file_location + "gstreamer/build && cd "+ file_location + "gstreamer/build; cmake ../; make -j4; make install; export GST_PLUGIN_PATH=/usr/local")
	# if ssh_dut.ssh_exec("gst-inspect-1.0 mfxdecode") <> "" and ssh_dut.ssh_exec("gst-inspect-1.0 mfxvpp") <> "" and ssh_dut.ssh_exec("gst-inspect-1.0 mfxsink") <> "":
	# 	print "GSTreamer Installed Successfully"
	# else:
	# 	print "GSTreamer Fail to install"
	# 	return False
	
	
	# Install Intel GPA
	ssh_dut.ssh_exec("mkdir " + file_location + "GPA/; mv " + file_location + "*.rpm " + file_location + "GPA/")
	ssh_dut.ssh_exec("rpm -ivh --nodeps " + file_location + "GPA/*.rpm ")
	# ssh_dut.ssh_exec("rpm -Ufh " + file_location + "GPA/*.rpm ")
	# if ssh_dut.ssh_exec("dmesg | grep -i gpa") == "":
	# 	print "There's no error(s) while installing GPA module"
	# else:
	# 	print "There's error(s) while installing GPA module"
	# 	return False
	
	# Install IAS a.k.a Weston
	ssh_dut.ssh_exec("mkdir " + file_location + "Weston/; mv " + file_location + "weston-*.rpm " + file_location + "Weston/")
	ssh_dut.ssh_exec("rpm -ivh --nodeps " + file_location + "Weston/*.rpm")
	installed_rpm_list = ssh_dut.ssh_exec("rpm -qa")
	# for i in splitter_comma.split(ssh_dut.ssh_exec("ls " + file_location + "Weston/ | grep -i rpm" )):
	# 	rpm_package = splitter_rpmext.split(i)[0]
	# 	if rpm_package in installed_rpm_list:
	# 		print rpm_package + " available"
	# 	else:
	# 		print rpm_package + " not available"
	# 		return False
	return True

def uninstall_rpms():
	print ssh_dut.ssh_exec("ls " + file_location + "UFO | grep -i rpm" )
	for i in splitter_comma.split(ssh_dut.ssh_exec("ls " + file_location + "UFO| grep -i rpm" )):
		uninstall_rpm_list.append(splitter_rpmext.split(i)[0])
				
	for i in splitter_comma.split(ssh_dut.ssh_exec("ls " + file_location + "MediaSDK | grep -i rpm" )):
		uninstall_rpm_list.append(splitter_rpmext.split(i)[0])
			
	for i in splitter_comma.split(ssh_dut.ssh_exec("ls " + file_location + "GPA | grep -i rpm" )):
		print i
		uninstall_rpm_list.append(splitter_rpmext.split(i)[0])
		
	for i in splitter_comma.split(ssh_dut.ssh_exec("ls " + file_location + "Weston | grep -i rpm" )):
		uninstall_rpm_list.append(splitter_rpmext.split(i)[0])
	print uninstall_rpm_list
	uninstall_list = " " .join(uninstall_rpm_list)
	if ssh_dut.ssh_exec("rpm -e " + uninstall_list):
		print "Successful uninstall all rpms"
		verdict = True
	else:
		print "Fail uninstall all rpms"
		verdict = False
	
	return verdict
		
def main():
	
	if operation == "pull":
		verdict = pull_rpm()
	elif operation == "install":
		copy_rpms()
		verdict = install_rpms()
	elif operation == "uninstall":
		verdict = uninstall_rpms()
	elif operation == "copy_back":
		verdict = reverse_copy()
		
	if verdict == True:
		print "Final Test Verdict : PASS"
		sys.exit(0)
	else:
		print "Final Test Verdict : FAIL"
		sys.exit(1)
	
main()