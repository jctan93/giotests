## Part of an automation script that initiates clock & playback & also recording for comparison
## Part Author: Henri Ngui (WWID 11472439)

## UPDATE 2013-11-09: Added slave loopback functionality

## UPDATE 2013-12-08: Finalize the script

## UPDATE 2013-12-18: Added additional flags for changes from LPE_script3a.sh to LPE_script4.sh parameter.
## Additional 2 paramters (driver, file selection option)

import os
import sys
import string
import re
import time
import argparse
import GenericCommand
import Result_Parser
#import getopt
from datetime import date, datetime

script_name = str(sys.argv[0])

## SETTING DEFAULT VARIABLES
#host_ip = "172.30.248.190"
driver = "IAFW"
sut1_ip = "172.30.248.22"
sut1_port = "2300"
sut2_ip = "172.30.248.111"
sut2_port = "2300"
autoear_server = "172.30.248.166"
ssp0_clk = "tdm"
ssp1_clk = "tdm"
ssp2_clk = "tdm"
test_audio = "/home/Music/ORI_files-LPE-auto/"
test_audio2 = ""
test_mode = "master"

lpe_script = "/home/Music/LPE_script4.sh"

usage="This script executes LPE playback and recording over the network.\n"

parser = argparse.ArgumentParser(prog = script_name, description = usage)
parser.add_argument('-i', help='SUT 1 IP for test')
parser.add_argument('-j', help='SUT 2 IP to provide clock')
parser.add_argument('-d', help='Driver [ IAFW | IA ]')
parser.add_argument('-ssp0', help='SSP0 port [ tdm | i2s ]')
parser.add_argument('-ssp1', help='SSP1 port [ tdm | i2s ]')
parser.add_argument('-ssp2', help='SSP2 port [ tdm | i2s ]')
#parser.add_argument('-p0', help='Enable SSP0 port test')
#parser.add_argument('-p1', help='Enable SSP1 port test')
#parser.add_argument('-p2', help='Enable SSP2 port test')
parser.add_argument('-f', help='Audio file directory')
parser.add_argument('-f2', help='Audio file directory for SSP2')
parser.add_argument('-m', help='Test mode [ master | slave_header_loopback | txrx_slave_playback | txrx_slave_record | custom ]')
parser.add_argument('-debug', help='Flag to enable debug mode when inserted True')

args = parser.parse_args()

## LOGIN & INITIALIZATION
if args.i is not None:
    sut1_ip = args.i
    dut1 = GenericCommand.GenericCommand()
    dut1.login(sut1_ip,sut1_port)
	
if args.j is not None:
    sut2_ip = args.j
    dut2 = GenericCommand.GenericCommand()
    dut2.login(sut2_ip,sut2_port)

if args.d is not None:
    driver = str(args.d)
    
if args.ssp0 is not None:
    ssp0_clk = str(args.ssp0)
    ssp0_port = "SSP0"
else:
    ssp0_port = ""
    #print "Please define SSP0 is TDM or I2S"
    #sys.exit(1)
    
if args.ssp1 is not None:
    ssp1_clk = str(args.ssp1)
    ssp1_port = "SSP1"
else:
    ssp1_port = ""
    #print "Please define SSP1 is TDM or I2S"
    #sys.exit(1)
    
if args.ssp2 is not None:
    ssp2_clk = str(args.ssp2)
    ssp2_port = "SSP2"
else:
    ssp2_port = ""
    #print "Please define SSP2 is TDM or I2S"
    #sys.exit(1)

# if args.p0 is not None:
    # ssp0_port = "SSP0"
# else:
    # ssp0_port = ""
    
# if args.p1 is not None:
    # ssp1_port = "SSP1"
# else:
    # ssp1_port = ""

# if args.p2 is not None:
    # ssp2_port = "SSP2"
# else:
    # ssp2_port = ""

if args.f is not None:
    test_audio = str(args.f)
if args.f2 is not None:
    test_audio2 = str(args.f2)
    
if args.m is not None:
    test_mode = str(args.m)

debug = False
if args.debug is not None:
    debug = True

# try: 
    # opts, args = getopt.getopt(sys.argv[1:], '', ['debug'])
    # for opt, arg in opts:
        # if opt == '--debug':
            # debug == True

# except StandardError , e:
    # print e

## SELECTIONS & EXECUTIONS

## txrx_slave_record mode is used for testing SLAVE SUT recording. The clock signal is provided by the MASTER SUT
## Playback is done on the MASTER SUT after recording has been initiated on the SLAVE SUT.
## Use of loopback jumper cables are necessary between both SUT headers.
if debug:
    print "LPE_automation.py: Test mode selected - " + test_mode

if test_mode == "txrx_slave_record":
    ## Execute playback on master SUT to provide clock to slave SUT
    if args.j is None:
        print "LPE_automation.py: Please define Master SUT IP"
        sys.exit(1)
        
    # Gold files are to be selected according to mode before playback on Slave SUT.
    if ssp0_clk == "i2s" or ssp1_clk == "i2s" or ssp2_clk == "i2s":
        test_audio2 = "/home/Music/48KHz_24_stereo.wav"
    else:
        test_audio2 = "/home/Music/TDM8/8ch_32.wav"
        #test_audio2 = "/home/Music/8ch_48Khz_24_Billionaire.wav"
    
    ## Start the clock signal on the Master SUT
    print dut2.timeexecute("bash " + lpe_script + " " + driver + " " + ssp0_clk + " " + ssp1_clk + " " + ssp2_clk + " arecord test " + ssp0_port + " " + ssp1_port + " " + ssp2_port)
    if debug:
        print "LPE_automation.py: Recording on Master SUT (Clock signal) has started..."
    
    ## Start the recording on the Slave SUT
    print dut1.timeexecute("bash " + lpe_script + " " + driver + " " + ssp0_clk + " " + ssp1_clk + " " + ssp2_clk + " arecord test " + ssp0_port + " " + ssp1_port + " " + ssp2_port)
    if debug:
        print "LPE_automation.py: Recording on the Primary SUT has started..."
    
    ## Start the playback on the Master SUT
    print dut2.timeexecute("bash " + lpe_script + " " + driver + " " + ssp0_clk + " " + ssp1_clk + " " + ssp2_clk + " aplay test " + ssp0_port + " " + ssp1_port + " " + ssp2_port + " " + test_audio)
    if debug:
        print "LPE_automation.py: Playback on the Master SUT has started..."


## txrx_slave_playback mode is used for testing SLAVE SUT recording. The clock signal is provided by the MASTER SUT
## Playback is done on the SLAVE SUT after the recording has been started on the MASTER SUT.
## Use of loopback jumper cables are necessary between both SUT headers.
elif test_mode == "txrx_slave_playback":
    ## Execute playback & recording. Produce recorded audio.
    if args.j is None:
        print "LPE_automation.py: Please define Master SUT IP"
        sys.exit(1)
    
    # Gold files are to be selected according to mode before playback on Slave SUT.
    if ssp2_port == "i2s":
        test_audio2 = "/home/Music/48KHz_24_stereo.wav"
    else:
        test_audio2 = "/home/Music/TDM8/8ch.wav"
        #test_audio2 = "/home/Music/8ch_48Khz_24_Billionaire.wav"
    
    dut2.timeexecute("bash " + lpe_script + " " + driver + " " + ssp0_clk + " " + ssp1_clk + " " + ssp2_clk + " arecord test " + ssp0_port + " " + ssp1_port + " " + ssp2_port)
    if debug:
        print "LPE_automation.py: Recording on Master SUT (Clock Signal) has started..."
        print "LPE_automation.py: Playback on Slave SUT has started..."
    dut1.timeexecute("bash " + lpe_script + " " + driver + " " + ssp0_clk + " " + ssp1_clk + " " + ssp2_clk + " arecord_aplay test " + ssp0_port + " " + ssp1_port + " " + ssp2_port + " " + test_audio)

## slave_header_loopback is used for SLAVE SUT to playback & record using loopback from the same SSP port itself.
## While the clock is provided by the MASTER SUT.
## The MASTER SUT must provide clock 1st before the SLAVE SUT can perform recording & playback.
elif test_mode == "slave_header_loopback":

    ## Execute playback on master SUT to provide clock to slave SUT
    if ssp2_port == "i2s":
        test_audio2 = "/home/Music/48KHz_24_stereo.wav" # Check SUT side for presence of file
    else:
        test_audio2 = "/home/Music/TDM8/8ch_32.wav" # Check SUT side for presence of file
        #test_audio2 = "/home/Music/8ch_48Khz_24_Billionaire.wav"
    
    if debug:    
        print "LPE_automation.py: Playback on Master SUT (Clock Signal) has started..."
        print sut2_ip + ": " + lpe_script + " " + driver + " " + ssp0_clk + " " + ssp1_clk + " " + ssp2_clk + " aplay test " + ssp0_port + " " + ssp1_port + " " + ssp2_port

    dut2.timeexecute("bash " + lpe_script + " " + driver + " " + ssp0_clk + " " + ssp1_clk + " " + ssp2_clk + " aplay test " + ssp0_port + " " + ssp1_port + " " + ssp2_port)

    ## Execute playback & recording. Produce recorded audio.
    if debug:
        print "LPE_automation.py: Recording and playback on Primary SUT has started..."
        print sut1_ip + ": " + lpe_script + " " + driver + " " + sut1_ip + " " + ssp0_clk + " " + ssp1_clk + " " + ssp2_clk + " arecord_aplay test " + ssp0_port + " " + ssp1_port + " " + ssp2_port + " " + test_audio
        
    dut1.timeexecute("bash " + lpe_script + " " + driver + " " + ssp0_clk + " " + ssp1_clk + " " + ssp2_clk + " arecord_aplay test " + ssp0_port + " " + ssp1_port + " " + ssp2_port + " " + test_audio)

## Reserved space for custom scripts
elif test_mode == "custom":
    print "This test mode needs to be manually scripted & is non constant. Usage of this mode may break the script"
    sys.exit(1)
    
## MASTER MODE is used for TDM master & I2S master mode to do playback & recording. This mode runs on the PRIMARY SUT only.
else: # MASTER MODE
    if debug:
        print "LPE_automation.py: Playback and recording on SUT has started..."
        print sut1_ip +  ": " + lpe_script + " " + driver + " " + ssp0_clk + " " + ssp1_clk + " " + ssp2_clk + " arecord_aplay test " + ssp0_port + " " + ssp1_port + " " + ssp2_port + " " + test_audio + " " + test_audio2
    
    dut1.timeexecute("bash " + lpe_script + " " + driver + " " + ssp0_clk + " " + ssp1_clk + " " + ssp2_clk + " arecord_aplay test " + ssp0_port + " " + ssp1_port + " " + ssp2_port + " " + test_audio + " " + test_audio2)

## Inject script into test SUT to send recorded wav file
dut1.execute("echo -e \"import GenericCommand\\n\\nthm = GenericCommand.GenericCommand()\\nthm.login(\\\"" + autoear_server + "\\\",\\\"2300\\\")\" > /home/Music/send_audio_file.py")
if args.ssp0 is not None:
    dut1.execute("echo -e \"\\nthm.timefiletransfer(\\\"/home/SSP0_" + ssp0_clk + ".wav\\\",\\\"c:/temp/SSP0_" + ssp0_clk + ".wav\\\")\" >> /home/Music/send_audio_file.py")
if args.ssp1 is not None:
    dut1.execute("echo -e \"\\nthm.timefiletransfer(\\\"/home/SSP1_" + ssp1_clk + ".wav\\\",\\\"c:/temp/SSP1_" + ssp1_clk + ".wav\\\")\" >> /home/Music/send_audio_file.py")
if args.ssp2 is not None:
    dut1.execute("echo -e \"\\nthm.timefiletransfer(\\\"/home/SSP2_" + ssp2_clk + ".wav\\\",\\\"c:/temp/SSP2_" + ssp2_clk + ".wav\\\")\" >> /home/Music/send_audio_file.py")

time.sleep(25)
## Stop recording on test SUT
dut1.timeexecute("bash /home/Music/killa.sh")
if debug:
    print "LPE_automation.py: Playback and recording killed"
time.sleep(2) # Necessary only for playback. Recording has duration set.
## Stop playback on master SUT providing clock
if args.j is not None:
    dut2.timeexecute("bash /home/Music/killa.sh")
if test_mode == "slave":
    if debug:
        print "LPE_automation.py: Playback on Master SUT terminated!"
## Send audio recording file to autoEar Windows host for comparison & verdict
if debug:
    print "LPE_automation.py: Executing file transfer..."
dut1.execute("python /home/Music/send_audio_file.py")
if debug:
    print "LPE_automation.py: File transfer complete"
dut1.execute("mkdir /home/old/")
dut1.execute("mv -f /home/SSP*.wav /home/old/")
if debug:
    print "LPE_automation.py: Execution part completed."
sys.exit(0)
