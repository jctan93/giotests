import os, sys, json, subprocess, re, time, multiprocessing, argparse
from ssh_util import *
from datetime import date

source_list = ["Internal", "External"]
kernel_list = ["CAVS-HD", "CAVS-SSP", "Legacy-HD"]
category_list = ["core-image-sato-sdk", "core-image-sato", "linux-kenel", "custom"]

script_name = str(sys.argv[0])
usage="Build Image Script. \n"
parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-sut_ip', help='-sut_ip 172.30.249.86 a.k.a build machine IP')
parser.add_argument('-thm_ip', help='-thm_ip 172.30.249.86')
parser.add_argument('-s', metavar='--source', help='\n1. Build Image from IOTG PED Server.\n2. Build Image from external source(Default)')
parser.add_argument('-k', metavar='--kernel', help='\n1. Build kernel image with CAVS HD Audio driver (Default)\n2. Build kernel image with CAVS SSP Audio driver.\n3. Build kernel image with legacy HD Audio driver')
parser.add_argument('-c', metavar='--cat', help='\n1. core-image-sato-sdk (Default)\n2. core-image-sato\n3. linux-kernel\n4. custom')
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip
else:
	print "sut_ip parameter missing. "
	sys.exit(1)

if args.thm_ip is not None:
	thm_ip = args.thm_ip
else:
	print "thm_ip parameter missing. "
	sys.exit(1)

if args.s is not None and args.k is not None and args.c is not None:
	source = str(args.s)
	kernel = str(args.k)
	cat = str(args.c)
else:
	source = "2"
	kernel = "1"
	cat = "1"

root_location = "/home/swbkc/"
image_desired_location = root_location + "build/yocto/bxt/" + str(date.today().year) + "/GIO/"
image_configname_location = image_desired_location + source_list[int(source)-1] + "_"+ kernel_list[int(kernel)-1] + "_"+ category_list[int(cat)-1] + "/"
image_location = image_configname_location + "yocto_build/build/tmp/deploy/images/intel-corei7-64-cavs-hda/"
log_location = image_configname_location + "yocto_build/build/tmp/log/cooker/intel-corei7-64/"
bsp_location = image_configname_location + "bsp/"

ssh_sut = ssh_com(sut_ip, user = "swbkc")
ssh_sut.setpub(sshpass="intel!@#")
ssh_thm = ssh_com(thm_ip)
ssh_thm.setpub(sshpass="bxtroot")

def main():
	ssh_sut.ssh_exec("mkdir "+ image_configname_location)
	ssh_sut.ssh_exec("mkdir "+ image_configname_location + "bsp")
	ssh_sut.ssh_exec("tar --strip-components=1 -xf " + image_desired_location + "*.tar.bz2 -C " + image_configname_location + "bsp/")
	verdict = ssh_sut.ssh_exec("python " + root_location + "image_build.py -loc " + bsp_location +" -s " + source + " -k " + kernel + " -t " + cat)
	if "Image successfully generated" in verdict:
		print image_desired_location + source_list[int(source)-1] + "_"+ kernel_list[int(kernel)-1] + "_"+ category_list[int(cat)-1] + " Image : Success"
		sys.exit(0)
	else:
		print image_desired_location + source_list[int(source)-1] + "_"+ kernel_list[int(kernel)-1] + "_"+ category_list[int(cat)-1] + " Image : Fail"
		sys.exit(1)

main()