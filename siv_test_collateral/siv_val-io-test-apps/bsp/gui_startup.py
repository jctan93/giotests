import os, sys, time, platform, argparse

script_name = str(sys.argv[0])
usage = "This is yocto detail test"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-op', help='Operation = [matchbox, xterm]')
args = parser.parse_args()

if args.op is not None:
	operation = args.op
	if operation == "matchbox":
		os.system("sed -i '/matchbox-session/s/^#//g' ~/.xinitrc; sed -i '/xterm/s/^/#/g' ~/.xinitrc") # comment out the xterm option, uncomment matchbox
	elif operation == "xterm":
		os.system("sed -i '/xterm/s/^#//g' ~/.xinitrc; sed -i '/matchbox-session/s/^/#/g' ~/.xinitrc") # comment out the xterm option, uncomment matchbox

plat_name = platform.platform()
plat_hostname = platform.node()
release_ver = platform.version()
print "Print SUT & Image Info "
print "=================================="
print "Machine Name: " + plat_hostname
print "Platform Name: " + plat_name
print "Release Version: " + release_ver
print "==================================\n\n"
print "=================================="
print "Execute Graphical User Interface Startup Test"
# os.system("echo \"exec matchbox-session\" > /home/root/.xinitrc")
os.system("startx &")
os.system("export DISPLAY=:0")
os.system("glxinfo | grep -i OpenGL >> /opengl.log")
time.sleep(30)
verdict = os.system("ps -e | grep " + operation)

# if operation == "matchbox":
# 	os.system("sed -i '/xterm/s/^#//g' ~/.xinitrc; sed -i '/matchbox-session/s/^/#/g' ~/.xinitrc") # comment out the matchbox option, uncomment xterm
	
if verdict == 0:
    test = "PASS"
    print "Test Result:" + test
    print "==================================\n\n"
    os.system("killall X")
    time.sleep(30)
    sys.exit(0)
else: 
    test = "FAIL"   
    print "Test Result:" + test
    print "==================================\n\n"
    os.system("killall X")
    time.sleep(30)
    sys.exit(1) 

