import os, re, sys, json, time, argparse, datetime, httplib2, math, glob
from ssh_util import *

# global declaration of test script and apps location
test_case_key_name = {'pull':'pull_image', 'setup':'setup', 'imd':'install_misc_dependencies', 'master_slave_interchange':'master_slave_interchange', 'ipc':'install_proprietary_contents'}
bxt_daily_automation_location = "/root/BXT_Daily_Automation/"
gvruns_location = "/usr/local/gv/var/gvruns/"
file_location =  max(glob.glob(os.path.join(gvruns_location, '*/')))
test_app_location = file_location + "siv_val-io-test-apps"
script_location = file_location + "siv_val-io-test-scripts"
# 	Working hostname without trigger GPIO.py
hostname_link = "http://pglvm2008-v03.png.intel.com/releases/hostname/hostname-20170622_231453.zip"
multiple_splitter = re.compile("->|../|-|.hddimg")
#	global declaration for global variable
list_container = []
dict_container = {}
FileDl = []

script_name = str(sys.argv[0])
usage = "This is Downloading, Cloning Image and Install Misc. Dependencies"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-minno_ip', help='MINNO IP')
parser.add_argument('-master', help='Master Disk ID')
parser.add_argument('-slave', help='Slave Disk ID')
parser.add_argument('-img_type', default = "hddimg", help='Image Type ["hddimg - default", "iso", "bzImage", "bsp"]')
parser.add_argument('-op', help='Operation ["pull", "setup", "imd", "master_slave_interchange", "ipc"]', required = True)
parser.add_argument('-cat', default = "dev",help='Image Category ["dev", "stable"]')
args = parser.parse_args()

if args.op is not None:
	operation = args.op
	if operation == "pull":
		if args.img_type is not None:
			replace_target = args.img_type 
			if args.cat is not None:
				image_category = args.cat
				if image_category == "dev":
					build_name = "BXT-LINUX-YOCTO.BSP_DEV"
				elif image_category == "stable":
					build_name = "BXT-LINUX-YOCTO.BSP_STABLE"
	elif operation in ["setup","imd","master_slave_interchange", "ipc"]:
		if args.sut_ip is not None:
			sut_ip = args.sut_ip
		if args.minno_ip is not None:
			minno_ip = args.minno_ip
		if args.master is not None:
			master_id = args.master
		if args.slave is not None:
			slave_id = args.slave
	else:
		print "Invalid operation mode. Please check with the help option"
		sys.exit(1)

def pull_image():
	splitter_forwardslash = re.compile("/")
	cur_dir = os.path.dirname(os.path.abspath(__file__))
	# {"@latest":{"$eq":"true"}}
	content = """items.find({
			"$and":[
					{"repo":{"$eq":"ped-bxt-local"}},
					{"@build.name":{"$eq":""" +'"' + build_name + '"' + """}}					
			]})"""
	
	#httplib2.debuglevel = 1
	RepoUrl = "https://ubit-artifactory-ba.intel.com/artifactory/"
	apiPath = "api/search/aql"
	Uri = os.path.join(RepoUrl,apiPath)
	h = httplib2.Http(disable_ssl_certificate_validation=True)
	auth = "Ynh0X3ZhbF9hdXRvOml0aXNjb29sMTUh"
	resp, content = h.request(Uri,'POST',headers = {'Authorization' : 'Basic ' + auth},body = content)
	#convert string content to json
	content = json.loads(content)
	if resp["status"] == "200":
		result_list = content["results"]
		for result in result_list:
			if isinstance(result,dict):
				Repo = result["repo"]
				Path = result["path"]
				File = result["name"]
			
			if replace_target in ["hddimg", "iso"]:
				folder_name = "latest_img"
				json_file = "img_loc.json"
			elif replace_target == "bsp":
				folder_name = "latest_bsp"
				json_file = "bsp_loc.json"
				
			if replace_target == "hddimg" and "hddimg.tar.bz2" in File:
				FileDl.append(os.path.join(RepoUrl,Repo,Path,File))				
			if replace_target == "hddimg" and "hddimg.tar.bz2" not in File:
				continue
			elif replace_target == "iso" and "iso.tar.bz2" not in File:
				continue
			elif replace_target == "bzImage" and "bzImage" not in File:
				continue
			elif replace_target == "bsp" and "intel-apollolake-i-jethro" in File and "tar.bz2" in File:
				FileDl.append(os.path.join(RepoUrl,Repo,Path,File))
				
		FilePrefix = os.path.join(cur_dir,folder_name)
		FileAbsPath = os.path.join(FilePrefix,splitter_forwardslash.split(FileDl[-1])[-1])
		with open(os.path.join(cur_dir, json_file)) as json_data:
			img_loc = json.load(json_data)
			if FileDl[-1] != img_loc[0]['download_link']:
				print image_category + " track image."
				print "Removing previous hddimg file"
				os.system("rm -rf " + os.path.join(cur_dir,folder_name,"*"))
				print "Downloading latest image"
				status = os.system("wget --quiet --no-check-certificate --directory-prefix=" + FilePrefix + " -nc " + FileDl[-1])
				if status != 0:
					print "Failed to download " + File
					sys.exit(1)
				
				# checking if it image is compressed to tarball and untar
				if "tar.bz2" in FileDl[-1]:
					print "Untarring Image from tarball.."
					os.system("tar --strip-components=1 -xf " + FileAbsPath + " -C " + FilePrefix)
				
				#added by William 13 Sept 2016
				dict_container['download_link'] = FileDl[-1]
				list_container.append(dict_container)
				with open(os.path.join(cur_dir,json_file), 'w+') as outfile:
					json.dump(list_container, outfile)					
				encoded = json.dumps(list_container,indent=4,sort_keys=True)
				sys.exit(0)
			else:
				print "This is not the latest " + image_category + " track image."
				print "Track image again in 1 mins"
				time.sleep(60)					
				pull_image()					
	else:
	   print "Error response status --> " + resp["status"]     
	   print resp
	   sys.exit(1)
	  
def get_disk_id(ssh_agent):
	master_command = "ls -l /dev/disk/by-id | grep -i " + str(master_id) + " | grep -v part"
	master_label = "/dev/" + str(multiple_splitter.split(ssh_agent.ssh_exec(master_command, verbose=False))[-1])
	slave_command = "ls -l /dev/disk/by-id | grep -i " + str(slave_id) + " | grep -v part"
	slave_label = "/dev/" + str(multiple_splitter.split(ssh_agent.ssh_exec(slave_command, verbose=False))[-1])
	if "mmc" in master_label:
		master_label += "p"
	if "mmc" in slave_label:
		slave_label += "p"	
	print "\nMaster Label : " + master_label + "\nSlave Label : " + slave_label + "\n"
	return (master_label, slave_label)

def setup():
	ssh_agent = ssh_com(sut_ip)
	ssh_agent.setpub(sshpass="")
	if ssh_agent.chk_con():
		ssh_minno = ssh_com(minno_ip)
		ssh_minno.setpub(sshpass="bxtroot")
		print "Minno IP: " + minno_ip + "\nSUT IP: " + sut_ip + "\n"
		(master_label, slave_label) = get_disk_id(ssh_agent)
		if ssh_agent.ssh_exec("ls / | grep MASTER", verbose=False):
			from_minno = ssh_minno.ssh_exec("md5sum " + bxt_daily_automation_location + "latest_img/*.hddimg", verbose=False)
			from_master = ssh_agent.ssh_exec("md5sum /latest_img/*.hddimg", verbose=False)
			print "\nArtifactory Image MD5SUM : " + multiple_splitter.split(from_minno)[0] + "\nMaster Image MD5SUM : " + multiple_splitter.split(from_master)[0] + "\n"
			if multiple_splitter.split(from_minno)[0] != multiple_splitter.split(from_master)[0]:
				ssh_agent.ssh_exec("rm -rf /latest_img/*; rm -rf /clone.log")
				ssh_minno.ssh_exec("scp -r " + bxt_daily_automation_location + "latest_img/*.hddimg root@" + sut_ip + ":/latest_img/.")
				start_time  = time.time()
				ssh_agent.ssh_exec("/mkefidisk.sh " + slave_label + " /latest_img/" + ssh_agent.ssh_exec("ls /latest_img/", verbose=False) + " " + slave_label + " >> /clone.log")
				end_time = time.time()
				difference_time = end_time - start_time
				if "Installation completed successfully" in ssh_agent.ssh_exec("cat /clone.log", verbose=False):
					print "Time Cloning Image : approx. " + str(math.ceil(difference_time/60)) + " minutes"
					print "Flash Image : PASS"
					master_slave_interchange()
					time.sleep(10)
					if ssh_agent.chk_con():
						print "SUT is live"
						ssh_agent.ssh_exec("wget " + hostname_link + "; unzip hostname-*.zip; python ~/hostname/hostname.py")
						time.sleep(60)
						if ssh_agent.chk_con() and "unknown-" in ssh_agent.ssh_exec("uname -a", verbose=False):
							print "Hostname Installation : PASS"
							sys.exit(0)
						else:
							print "Hostname Installation : FAIL"
							sys.exit(1)
					else:
						sys.exit(1)
				else:
					print "Flash Image : FAIL"
					sys.exit(1)
			else:
				print "This is up-to-date image. Proceed to exit."
				sys.exit(1)
		else:
			master_slave_interchange()
			setup()

def install_misc_dependencies():
	ssh_agent = ssh_com(sut_ip)
	ssh_agent.setpub(sshpass="")
	ssh_minno = ssh_com(minno_ip)
	ssh_minno.setpub(sshpass="bxtroot")
	kernel_version = multiple_splitter.split(ssh_agent.ssh_exec("uname -r", verbose=False))[0]
	if ssh_agent.chk_con():
		ssh_minno.ssh_exec("rm -rf /home/siv_test_collateral")
		ssh_agent.ssh_exec("mkdir /home/siv_test_collateral")
		ssh_minno.ssh_exec("mkdir /home/siv_test_collateral")
		os.system("scp -r " + test_app_location + " root@"+ sut_ip + ":/home/siv_test_collateral/siv_val-io-test-apps/")
		os.system("scp -r " + test_app_location + " root@" + minno_ip + ":/home/siv_test_collateral/siv_val-io-test-apps/")
		os.system("scp -r " + script_location + " root@" + minno_ip + ":/home/siv_test_collateral/siv_val-io-test-scripts/")
		ssh_agent.ssh_exec("cd /home/siv_test_collateral/siv_val-io-test-apps/smbus/i2c-tools-3.1.0/; make; make install")
		ssh_agent.ssh_exec("/home/siv_test_collateral/siv_val-io-test-apps/eth/ethtool-4.2/configure;make;make install")
		ssh_agent.ssh_exec("cd /home/siv_test_collateral/siv_val-io-test-apps/; make")
		ssh_agent.ssh_exec("sed -i '/^#/! {/add/ s/^/#/}' /etc/udev/rules.d/automount.rules; sync; sed -i '/^#/! {/remove/ s/^/#/}' /etc/udev/rules.d/automount.rules; sync; sed -i '/^#/! {/change/ s/^/#/}' /etc/udev/rules.d/automount.rules; sync")
		ssh_agent.ssh_exec("cp -r /home/siv_test_collateral/siv_val-io-test-apps/misc/generic-config/. /usr/lib/python2.7/site-packages/")
		ssh_minno.ssh_exec("cp -r /home/ped-bxt-release-proprietary-local/* /home/latest_ipu_rpms")
		if kernel_version >= "4.9" and "command not found" in ssh_agent.ssh_exec("smart", verbose=False):
			ssh_agent.ssh_exec("mkdir -p /etc/yum.repos.d; echo '' > /etc/yum.repos.d/oe-remote-repo-apl-rpm.repo; sed -i 'i[oe-remote-repo-apl-rpm]\\nname=OE Remote Repo: APL Pyro RPM\\nbaseurl=http:\/\/172.30.109.231\/apollolake_pyro\/CURRENT\/rpm' /etc/yum.repos.d/oe-remote-repo-apl-rpm.repo; dnf makecache; yes | dnf install tpm2.0-tss* --nogpgcheck; yes | dnf install jhi-tests --nogpgcheck; yes | dnf install expect --nogpgcheck")
		elif kernel_version >= "4.9" and "command not found" in ssh_agent.ssh_exec("dnf", verbose=False):
			ssh_agent.ssh_exec("/home/siv_test_collateral/siv_val-io-test-apps/smart_add.sh; smart update; yes | smart install jhi-tests tpm2.0-tss* expect")
		elif kernel_version < "4.9" and kernel_version >= "4.1" and "command not found" in ssh_agent.ssh_exec("smart", verbose=False):
			ssh_agent.ssh_exec("mkdir -p /etc/yum.repos.d; echo '' > /etc/yum.repos.d/oe-remote-repo-apl-rpm.repo; sed -i 'i[oe-remote-repo-apl-rpm]\\nname=OE Remote Repo: APL Pyro RPM\\nbaseurl=http:\/\/172.30.109.231\/apollolake_pyro\/CURRENT\/rpm' /etc/yum.repos.d/oe-remote-repo-apl-rpm.repo; dnf makecache; yes | dnf install tpm2.0-tss* --nogpgcheck; yes | dnf install jhi-tests --nogpgcheck; yes | dnf install expect --nogpgcheck")
		elif kernel_version < "4.9" and kernel_version >= "4.1" and "command not found" in ssh_agent.ssh_exec("dnf", verbose=False):
			ssh_agent.ssh_exec("/home/siv_test_collateral/siv_val-io-test-apps/smart_add.sh; smart update; yes | smart install jhi-tests tpm2.0-tss* expect")
		
		# ssh_agent.ssh_exec("systemctl enable gio.service; systemctl start gio.service") # incorperate with the latest hostname release(hostname-20170622_231453.zip)
		print ssh_agent.ssh_exec("uname -a", verbose=False)
		print "Dependencies Installation : PASS"
		ssh_agent.ssh_exec("reboot", verbose=False)
		if ssh_agent.chk_con():
			sys.exit(0)

def install_proprietary_contents():
	ssh_minno = ssh_com(minno_ip)
	ssh_minno.setpub(sshpass="bxtroot")
	if "Final Test Verdict : PASS" in ssh_minno.ssh_exec("python " + bxt_daily_automation_location + "ipu_pull_install.py -sut_ip " + sut_ip + " -thm_ip "+ minno_ip +" -op pull"):
		print "BXTN_IPU Download : PASS"
	else:
		print "BXTN_IPU Download : FAIL"
		sys.exit(1)
		
	if "Final Test Verdict : PASS" in ssh_minno.ssh_exec("python " + bxt_daily_automation_location + "ped-bxt-release-proprietary-local.py -sut_ip " + sut_ip + " -op pull"):
		print "Proprietary Content Download : PASS"
	else:
		print "Proprietary Content Download : FAIL"
		sys.exit(1)
		
	if "Final Test Verdict : PASS" in ssh_minno.ssh_exec("python " + bxt_daily_automation_location + "ipu_pull_install.py -sut_ip " + sut_ip + " -thm_ip " + minno_ip + " -op install"):
		print "BXTN_IPU Installation : PASS"
	else:
		print "BXTN_IPU Installation : FAIL"
		sys.exit(1)
		
	if "Final Test Verdict : PASS" in ssh_minno.ssh_exec("python " + bxt_daily_automation_location + "ped-bxt-release-proprietary-local.py -sut_ip " + sut_ip + " -op install"):
		print "Proprietary Content Installation : PASS"
	else:
		print "Proprietary Content Installation : FAIL"
		sys.exit(1)
	
	sys.exit(0)
	
def master_slave_interchange():
	ssh_agent = ssh_com(sut_ip)
	ssh_agent.setpub(sshpass="")
	(master_label, slave_label) = get_disk_id(ssh_agent)
	if ssh_agent.ssh_exec("ls / | grep MASTER", verbose=False):
		print "Slave booted" # need to terbalik it --> by right this is master USB
		ssh_agent.ssh_exec("mount "+ master_label +"1 /media && rm -rf /media/BOOT_MARKER", verbose=False) 
		ssh_agent.ssh_exec("sync", verbose=False)
		ssh_agent.ssh_exec("mount "+ slave_label +"1 /mnt && touch /mnt/BOOT_MARKER", verbose=False)
		ssh_agent.ssh_exec("sync", verbose=False)
		ssh_agent.ssh_exec("reboot", verbose=False)
	else:
		print "Master booted" # need to terbalik it --> by right this is slave USB
		ssh_agent.ssh_exec("mount " + master_label + "1 /media && touch /media/BOOT_MARKER", verbose=False)
		ssh_agent.ssh_exec("sync", verbose=False)
		ssh_agent.ssh_exec("mount " + slave_label + "1 /mnt && rm -rf /mnt/BOOT_MARKER", verbose=False)
		ssh_agent.ssh_exec("sync", verbose=False)
		ssh_agent.ssh_exec("reboot", verbose=False)

def master_image_depedencies_setup():
	ssh_agent = ssh_com(sut_ip)
	ssh_agent.setpub(sshpass="")
	(master_label, slave_label) = get_disk_id(ssh_agent)
	kernel_version = multiple_splitter.split(ssh_agent.ssh_exec("uname -r", verbose=False))[0]
	# copy test scripts and apps from git, run smart_add.sh
	ssh_agent.ssh_exec("mkdir /home/siv_test_collateral", verbose=False)
	ssh_agent.ssh_exec("mkdir /root/BXT_Daily_Automation", verbose=False)
	os.system("scp -r " + test_app_location + " root@"+ sut_ip + ":/home/siv_test_collateral/siv_val-io-test-apps/")
	os.system("scp -r " + script_location + " root@" + sut_ip + ":/home/siv_test_collateral/siv_val-io-test-scripts/")
	if kernel_version >= "4.9" and "command not found" in ssh_agent.ssh_exec("smart", verbose=False):
		ssh_agent.ssh_exec("mkdir -p /etc/yum.repos.d; echo '' > /etc/yum.repos.d/oe-remote-repo-apl-rpm.repo; sed -i 'i[oe-remote-repo-apl-rpm]\\nname=OE Remote Repo: APL Pyro RPM\\nbaseurl=http:\/\/172.30.109.231\/apollolake_pyro\/CURRENT\/rpm' /etc/yum.repos.d/oe-remote-repo-apl-rpm.repo; dnf makecache; yes | dnf install parted --nogpgcheck")
	elif kernel_version >= "4.9" and "command not found" in ssh_agent.ssh_exec("dnf", verbose=False):
		ssh_agent.ssh_exec("/home/siv_test_collateral/siv_val-io-test-apps/smart_add.sh; smart update; yes | smart install parted")
	elif kernel_version < "4.9" and kernel_version >= "4.1" and "command not found" in ssh_agent.ssh_exec("smart", verbose=False):
		ssh_agent.ssh_exec("mkdir -p /etc/yum.repos.d; echo '' > /etc/yum.repos.d/oe-remote-repo-apl-rpm.repo; sed -i 'i[oe-remote-repo-apl-rpm]\\nname=OE Remote Repo: APL Pyro RPM\\nbaseurl=http:\/\/172.30.109.231\/apollolake_pyro\/CURRENT\/rpm' /etc/yum.repos.d/oe-remote-repo-apl-rpm.repo; dnf makecache; yes | dnf install parted --nogpgcheck")
	elif kernel_version < "4.9" and kernel_version >= "4.1" and "command not found" in ssh_agent.ssh_exec("dnf", verbose=False):
		ssh_agent.ssh_exec("/home/siv_test_collateral/siv_val-io-test-apps/smart_add.sh; smart update; yes | smart install parted")
	
	# touch BOOT_MARKER at 1st partition and MASTER at /
	ssh_agent.ssh_exec("mount " + master_label + "1 /boot; touch /boot/BOOT_MARKER; touch /MASTER", verbose=False)
	# copy mkefidisk.sh to /
	ssh_agent.ssh_exec("cp -r /home/siv_test_collateral/siv_val-io-test-scripts/image_setup/mkefidisk.sh /", verbose=False)
	# print "Copy image setup, GPIO, ipu and proprietary scripts to /root/BXT_Daily_Automation"
	# ssh_agent.ssh_exec("cp -r /home/siv_test_collateral/siv_val-io-test-scripts/image_setup/* " + bxt_daily_automation_location, verbose=False)
	
def main():
	print "\n=========================== " + test_case_key_name[operation] + " Function ======================================="
	eval(test_case_key_name[operation])()
	print "\n=========================== End " + test_case_key_name[operation] + " Function =====================================\n"

main()