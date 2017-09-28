import os, re, sys, json, time, argparse, datetime, glob
from ssh_util import *

flag_verdict = []
test_app_folder = "/home/siv_test_collateral/siv_val-io-test-apps/IPU/sw_val/"
output_image_dir = test_app_folder + "output_image/"
gold_image_dir = test_app_folder + "gold_image/"
video_dir = test_app_folder + "video/"
test_app_script_dir = test_app_folder + "scripts/"
result_dir = test_app_folder + "results/"

script_name = str(sys.argv[0])
usage = "IPU Mondello Test Case"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
parser.add_argument('-thm_ip', help='THM IP')
parser.add_argument('-test_case', help='Test Case ID')
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip
if args.thm_ip is not None:
	thm_ip = args.thm_ip
if args.test_case is not None:
	test_case = args.test_case

ssh_agent = ssh_com(sut_ip)
ssh_agent.setpub(sshpass="")
ssh_thm = ssh_com(thm_ip)
ssh_thm.setpub(sshpass="bxtroot")

def record_transfer_segmented_video():
	print "Recording video for " + test_case
	ssh_agent.ssh_exec("export cameraInput=mondello", verbose=False)
	ssh_agent.ssh_exec("sed -i '/export/a export XDG_RUNTIME_DIR=/tmp/\nexport MONDELLO_SERVER_IP=172.30.249.126' /etc/profile")
	ssh_agent.ssh_exec("reboot")
	if ssh_agent.chk_con(timeout=60):
		ssh_agent.ssh_exec(test_app_script_dir + "gst_test.sh " + test_case, verbose=False)
		print "Copy video from SUT to THM for processing"
		ssh_thm.ssh_exec("scp -r root@" + sut_ip + ":" + result_dir + test_case + ".mp4 " + result_dir)
		print "Segmented video to screenshot"
		ssh_thm.ssh_exec("ffmpeg -i " + result_dir + test_case + ".mp4 " + output_image_dir + test_case + "_%03d.png -vframes 100")

def compare_image_frame():
	output_image_list = sorted(glob.glob(os.path.join(output_image_dir + test_case + "/", "*")))[0::10]
	gold_image_list = ssh_thm.ssh_exec("ls " + output_image_dir + test_case)
	for individual_image in output_image_list:
		result = ssh_thm.ssh_exec("compare -verbose -metric MAE " + individual_image + " " + gold_image_list + " null: 2>&1", verbose=False)
		if "all: 0 (0)" in result:
			flag_verdict.append("True")
		else:
			flag_verdict.append("False")
			
	if (flag_verdict[1:] == flag_verdict[:-1]) and ("True" in flag_verdict[:]):
		verdict = True
	else:
		verdict = False
	
	return verdict
		
def main():
	print "=========================== IPU Mondello Test Case ================================="
	print "Creating output folder for " + test_case
	ssh_agent.ssh_exec("mkdir " + output_image_dir + "; mkdir " + output_image_dir + test_case, verbose=False)
	record_transfer_segmented_video()
	# verdict = compare_image_frame()
	# if verdict:
	# 	print "IPU Mondello Test " + test_case + ": PASS"
	# 	sys.exit(0)
	# else:
	# 	print "IPU Mondello Test " + test_case + ": FAIL"
	# 	sys.exit(1)
	
main()