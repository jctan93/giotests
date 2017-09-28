import os, sys, json, netrc, base64, httplib2, subprocess, re, time, datetime, multiprocessing, argparse
from ssh_util import *

script_name = str(sys.argv[0])
usage="This program is to copy IPU RPM to SUT. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-sut_ip', help='-sut_ip 172.30.249.86')
parser.add_argument('-thm_ip', help='-thm_ip 172.30.249.86')
parser.add_argument('-op', help='Operation = [pull, install]')
args = parser.parse_args()

if args.sut_ip is not None and args.thm_ip is not None:
	sut_ip = args.sut_ip
	thm_ip = args.thm_ip

if args.op is not None:
	operation = args.op	

ssh_sut = ssh_com(sut_ip)
ssh_sut.setpub(sshpass="")
ssh_thm = ssh_com(thm_ip)
ssh_thm.setpub(sshpass="bxtroot")

def del_existing_ipu():
	dir = os.path.join("/home/latest_ipu_rpms/")
	os.system("rm -rf "+ dir +"*")

def ipu_rpm_pull():
	ipu_list = []
	aiqb_list = []
	icamsrc_list = []
	libcamhal_list = []
	libiaaiq_list= []
	libiacss_list = []
	# {"@latest_bkc":{"$eq":"true"}}
	verdict = "FAIL"
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
					{"repo":{"$eq":"ped-bxtn-ipu-local"}},
					{"@latest_bkc":{"$eq":"true"}}
				]})"""

    #httplib2.debuglevel = 1
	RepoUrl = "https://ubit-artifactory-ba.intel.com/artifactory/"
	apiPath = "api/search/aql"
	Uri = os.path.join(RepoUrl,apiPath)
	h = httplib2.Http(disable_ssl_certificate_validation=True)
	auth = base64.encodestring( login + ':' + password )
	resp, content = h.request(Uri,'POST',headers = { 'Authorization' : 'Basic ' + auth},body = content)
	
	#convert string content to json
	content = json.loads(content)
	if resp["status"] == "200":
		result_list = content["results"]
		for result in sorted(content["results"]):
			if isinstance(result,dict):	
				Repo = result["repo"]
				Path = result["path"]
				File = result["name"]
			
			FileDl = os.path.join(RepoUrl,Repo,Path,File)
			FilePrefix = os.path.join(cur_dir,"latest_ipu_rpms/")
			FileAbsPath = os.path.join(FilePrefix,File)
	
			#if FileDl.startswith("ipu4fw"):
			# For IPU
			if re.search("IPUFW_signed", FileDl) and not re.search("DSS", FileDl):
				# print "FileDl IPU : " + FileDl
				ipu_list.append(FileDl)
			# For aiqb
			if re.search("AIQB", FileDl):
				# print "FileDl : " + FileDl
				aiqb_list.append(FileDl)
			# for icamsrc
			if re.search("iCameraSrc", FileDl):
				# print "FileDl : " + FileDl
				icamsrc_list.append(FileDl)
			# for libcamhal
			if re.search("LibCamHal", FileDl):
				# print "FileDl : " + FileDl
				libcamhal_list.append(FileDl)
			#  for libIAAIQ
			if re.search("LibIAAIQ", FileDl):
				# print "FileDl : " + FileDl
				libiaaiq_list.append(FileDl)
			# 	libIACSS
			if re.search("LibIACSS", FileDl):
				# print "FileDl : " + FileDl
				libiacss_list.append(FileDl)
		
		ssh_sut.ssh_exec("wget --user "+ login +" --password " + password + " --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + ipu_list[-1])
		ssh_sut.ssh_exec("wget --user "+ login +" --password " + password + " --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + aiqb_list[-1])
		ssh_sut.ssh_exec("wget --user "+ login +" --password " + password + " --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + icamsrc_list[-1])
		ssh_sut.ssh_exec("wget --user "+ login +" --password " + password + " --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + libcamhal_list[-1])
		ssh_sut.ssh_exec("wget --user "+ login +" --password " + password + " --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + libiaaiq_list[-1])
		ssh_sut.ssh_exec("wget --user "+ login +" --password " + password + " --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + libiacss_list[-1])
		# transfer_cmd = "scp -r root@" + sut_ip + ":" + FilePrefix + "* " + FilePrefix
		# child = pexpect.spawn(transfer_cmd)
		# child.expect('yes/no')
		# child.sendline('yes')
		# child.read()
		verdict = True
	else:
		print "Error response status --> " + resp["status"]     
		print resp
		verdict = False
		
	return verdict

def ipu_installation():
	ssh_sut.ssh_exec("rpm -ivh --nodeps /home/latest_ipu_rpms/aiqb*.rpm")
	ssh_sut.ssh_exec("rpm -ivh --nodeps /home/latest_ipu_rpms/libiaaiq*.rpm")
	ssh_sut.ssh_exec("rpm -ivh --nodeps /home/latest_ipu_rpms/libiacss*.rpm")
	ssh_sut.ssh_exec("rpm -ivh --nodeps /home/latest_ipu_rpms/libcamhal*.rpm")
	ssh_sut.ssh_exec("rpm -ivh --nodeps /home/latest_ipu_rpms/icamerasrc*.rpm")
	ssh_sut.ssh_exec("rpm -ivh --nodeps /home/latest_ipu_rpms/ipu4fw*.rpm")
	return True

def main():
	if operation == "pull":
		del_existing_ipu()
		verdict = ipu_rpm_pull()
	elif operation == "install":
		verdict = ipu_installation()
	
	if verdict:
		print "\nFinal Test Verdict : PASS"
		sys.exit(0)

	else:
		print "\nFinal Test Verdict : FAIL"
		sys.exit(1)

main()
