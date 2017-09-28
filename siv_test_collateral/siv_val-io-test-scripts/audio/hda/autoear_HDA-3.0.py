#!/usr/bin/python


import os
import re
import sys
import getopt
import wave
import glob
import contextlib
import time
import traceback
import subprocess
import datetime
from threading import Thread
from datetime import *


def time_elapse(dur,task):

    counter = 0
    while counter <= dur:
       sys.stdout.write("\r" + task + " is elapsed " + str(counter))
       sys.stdout.flush()
       time.sleep(1)
       counter = counter + 1


def get_date():
    today = date.today()
    day = str(today.day)
    month = str(today.month)
    year = str(today.year)

    if(len(day)==1):
        day = "0" + day 
    if(len(month)==1):
        month = "0" + month

    currentDate = year +"." + month + "." + day
    return currentDate


def get_current_time():
   currentTime = datetime.time(datetime.now()) 
   time_Hour = currentTime.hour
   time_Minute = currentTime.minute
   time_Second = currentTime.second
   Time_now = str(time_Hour) + "." + str(time_Minute) + "." + str(time_Second)
   return Time_now



def logging(logfile,logmsg):

    logger = open(str(logfile),'a')
    logger.write("\n" + str(logmsg))
    logger.close()

    
def execute(comm=''):
    resp = ""
    if comm == '':
        print 'execute() Error: Argument is empty!'
        return False
    else:
        try:
            for stuff in os.popen(comm):
                resp += stuff
            return resp
        except:
            print 'execute() Error: Unable to execute command.'
            return False


def playing(duration,song):
   
    os.system("aplay -d " + str(duration) + " " + song)


def filetransfer_script(script_name,ori_loc,target_loc,obj,dest_ip,source_ip):
    myscript = """
import os
import time
import sys
from GenericCommand import *

thm = GenericCommand()
thm.login(\'""" + dest_ip + """\')
thm.timefiletransfer(\'""" + ori_loc + """\',\'""" + target_loc + """\')
filetrace = thm.timefiletrace(\'""" + target_loc + """\')"""

    obj = GenericCommand()
    obj.login(source_ip)
    obj.timefilescript(myscript,r"c:",script_name,".py")
    obj.execute("C:\\Python27\\python.exe C:\\" + script_name + ".py")
    #if os.path.isfile(target_loc):
    if obj.timefiletrace(target_loc):
          print target_loc + " successfully transmitted"
    else:
          print "failed to transmit " + target_loc
          sys.exit(1)

          
def filetransfer_script_linux(script_name,ori_loc,target_loc,obj,dest_ip,source_ip):
    obj = GenericCommand()
    obj.login(source_ip)
    #obj.timefilescript(myscript,r"/",script_name,".py")
    
    obj.execute("echo -e \"import os\nimport time\" > /" + script_name + ".py")
    obj.execute("echo -e \"import sys\nfrom GenericCommand import *\" >> /" + script_name + ".py")
    obj.execute("echo -e \"thm = GenericCommand()\nthm.login(\\\"" + dest_ip + "\\\")\" >> /" + script_name + ".py")
    obj.execute("echo -e \"thm.timefiletransfer(\\\"" + ori_loc + "\\\",\\\"" + target_loc + "\\\")\" >> /" + script_name + ".py")
    obj.execute("echo -e \"filetrace = thm.timefiletrace(\\\"" + target_loc + "\\\")\" >> /" + script_name + ".py")
    
    obj.execute("python /" + script_name + ".py")
    #if os.path.isfile(target_loc):
    if obj.timefiletrace(target_loc):
          print target_loc + " successfully transmitted"
    else:
          print "failed to transmit " + target_loc
          sys.exit(1)

          
def xfinder(filepath,filepattern,maxdepth):
 
    output = subprocess.check_output("find " + filepath + " -maxdepth " + str(maxdepth) + " -name " + filepattern,shell=True)
    output = output.strip()
    output = output.split("\n")
    if len(output) > 1:
         print "More than 1 file matched with specified file pattern " + filepattern + " and " + str(maxdepth) + " directory depth"
         logging(str(hdalog),"More than 1 file matched to specified file pattern" + filepattern + " and " + str(maxdepth) + "  directory depth")
         print output
         logging(str(hdalog),str(output))
         exit(1)
       
    elif len(output) == 1:
         return output[0]
    else:
         return ''



def result_parser(output,default_threshold):
    
    "Perform auto ear generated log result parsing"
    global dict
    global result_output
    dict = {}
    chl_list = []
    rate_list = []
    result_output = []
    date = ""
    verdict = True

    print "***Extracting result from AUTOEAR server***"
    for line in output:
         print line 
         if "Audio content size" in line:
                match_chl = re.search(r'channel \d',line)
                if match_chl:
                    chl_list.append(match_chl.group(0))
         
         elif "Total Similarity" in line:
                match_rate = re.search(r'\d+.\d+%',line)
                if match_rate:
                    rate_list.append(match_rate.group(0))
   
    print "Retrieving data....." 
    if not chl_list or not rate_list:
          print "***Failed to retrieve comparison result, the Audio Comparison App might has crashed***"
          sys.exit(1)
    else:
          print chl_list
          print rate_list
    time.sleep(5) 

    threshold_dict = {"0":threshold_ch0,"1":threshold_ch1}
    #Dictionary comprehension from Ang to map channel number to its respective similarity rate
    dict = { j:rate_list[i] for i,j in enumerate(chl_list)}
    for i,j in  dict.items():
        if "--threshold_ch" + i.split(" ")[-1] in opt_list:
	       threshold = threshold_dict[i.split(" ")[-1]]
        else:
               threshold = default_threshold
       
        if float(j[:-1]) < float(threshold) and float(threshold) > 0.0:
               print str(i) + " similarity :" +  str(j)  + " ,lower than " + str(threshold) + "%, Verdict: Failed"
               result_output.append(str(i) + " similarity :" +  str(j)  + " ,lower than " + str(threshold) + "%, Verdict: Failed")
               logging(hdalog,str(i) + " similarity :" +  str(j)  + " ,lower than " + str(threshold) + "%, Verdict: Failed")
               verdict = False
        elif float(threshold) <= 0.0:
               print str(i) + " similarity : NaN , Verdict: --"
               result_output.append(str(i) + " similarity : NaN , Verdict: Bypassed")
               logging(hdalog,str(i) + " similarity : NaN , Verdict: Bypassed")
               verdict = True
        else: 
               print str(i) +  " similarity :" + str(j) + " ,greater than " + str(threshold) + "%, Verdict: Passed"
               result_output.append(str(i) +  " similarity :" + str(j) + " ,greater than " + str(threshold) + "%, Verdict: Passed")
               logging(hdalog,str(i) +  " similarity :" + str(j) + " ,greater than " + str(threshold) + "%, Verdict: Passed")
    return verdict




if __name__ == '__main__':

    os.system("rm -rf /root/HDA.log")
    hdalog = "/root/HDA.log"

    autoduration = True
    output = "/output.wav"
    master = "50%"
    #it's advised to keep the capture volume at 80%
    capture = "80%"
    leftchnl = "50%"
    rightchnl = "50%"
    #PCM = "100%"
    source = 'Line'
    timeout = 10
    mp3 = False
    menu = False
    mute = False
    channel = False
    threshold_ch0 = None
    threshold_ch1 = None
    host_ip_add = "172.30.248.139" # MUST BE CHANGED ACCORING TO THM USED

    try:
    	   opts, args = getopt.getopt(sys.argv[1:], '', ['sutip=','thmip=','song=','rectime=','master=','capture=','output=','inputsource=','left=','right=','gold=','timeout=','threshold_ch0=','threshold_ch1=','mp3','help','mute'])
    	   for opt, arg in opts:
       	       if opt == '--sutip':
                   sutip = str(arg)
	       elif opt == '--thmip':
            	   thmip = str(arg)
               elif opt == '--song':
                   song = str(arg)
               elif opt == '--rectime':
                   rec_duration = str(arg)
                   autoduration = False
               elif opt == '--master':
                   master = str(arg)
                   if "%" not in master:
                      print "Input Error, please include '%' for master volume control"
                      sys.exit(1) 
               elif opt == '--capture':
                   capture = str(arg)
                   if "%" not in capture:
                      print "Input Error, please include '%' for capture volume control"
                      sys.exit(1) 
               elif opt == '--threshold_ch0':
                   threshold_ch0 = str(arg)
                   print "Channel 0's threshold set as: " + str(threshold_ch0) 
               elif opt == '--threshold_ch1':
                   threshold_ch1 = str(arg)
                   print "Channel 1's threshold set as: " + str(threshold_ch1) 
               elif opt == '--output':
                   output = str(arg)
               elif opt == '--inputsource':
                   source = str(arg)
               elif opt == '--gold':
                   gold = str(arg)
               elif opt == '--timeout':
                   timeout = int(arg)
               elif opt == '--left':
                   channel = True
                   leftchnl = str(arg)
                   if "%" not in leftchnl:
                      print "Input Error, please include '%' for left channel volume control"
                      sys.exit(1) 
               elif opt == '--right':
                   channel = True
                   rightchnl = str(arg)
                   if "%" not in rightchnl:
                      print "Input Error, please include '%' for right channel volume control"
                      sys.exit(1) 
               elif opt == '--mp3':
                   mp3 = True
                   autoduration = False
               elif opt == '--help':
                   menu == True
               elif opt == '--mute':
                   mute = True
              
                   
    except StandardError , e:
           print e
           print "try --help to get some clues"
 

    if menu:
       print """python <script name>  <args>
  list of Arguments
  =======================================
   --sutip       ==> to set SUT ip                            (mandatory)
                                  
   --thmip       ==> to set THM ip                            (mandatory)
                                  
   --song        ==> to specify refer song                    (mandatory)

   --gold        ==> to specify gold file name and directory  (mandatory)
                                  
   --rectime     ==> to set record duration                   (optional) ### no default value ###
             
   ***if rectime not specified, auto song length estimation will be implemented***
                                  
   --master      ==> to specify master volume                 (optional) ### default: 50% ###

   --capture     ==> to specify recording volume              (optional) ### default: 50% ###

   --left        ==> to specify left channel volume           (optional) ### default: 50% ###

   --right       ==> to specify right channel volume
                               
   --output      ==> to specify output file name and directory(optional) ### default: /output.wav ###
   
   --inputsource ==> to specify input source                  (optional) ### default: Line ###
   
   ***For inputsource,Front Mic and Rear Mic has to be specify like in following exp --inputsource "Front\ Mic"

   --timeout     ==> to specify time out duration             (optional) ### default: 30 ###
  
   --mp3         ==> to playback song in mp3 format           (optional) ### no arg value ###

   --mute        ==> to mute playback                         (optional) ### no arg value ###

   --help        ==> to view list of arguments                (optional) ### no arg value ###"""

       sys.exit(0) 

 

    #check if all mandatory aruguments has been defined
    opt_list = []
    for i in opts:
         opt_list.append(i[0]) 

    
    #Check GenericCommand readyness

    if os.path.isfile("/usr/lib/python2.7/site-packages/GenericCommand.py"):
         print "GenericCommand.py exists"
         logging(str(hdalog),"GenericCommand.py is exists")
         from GenericCommand import *
    else:
         temp = xfinder("/usr/local/gv","*Command.py",20)
         if temp != '':
             os.system("cp -r " + temp + " /usr/lib/python2.7/site-packages")
             print temp + " successfully copied"
             logging(str(hdalog),temp + "successfully copied to site-packages")
             from GenericCommand import *
         else:
             print "GenericCommand not found, temp is " + temp
             logging(str(hdalog),"GeneriCommand not found, temp is " + temp)
             sys.exit(1)



    worker1 = GenericCommand()
    print "SUT ip = " + sutip
    worker1.login(sutip) 
    print thmip 
    print sutip

    worker1.execute("pulseaudio --start")

    filetransfer_script("transfer_linein","C:\\lineInOri.wav","//lineInOri.wav","thm",sutip,thmip)
    time.sleep(3)
    filetransfer_script("transfer_micin","C:\\micInOri.wav","//micInOri.wav","thm",sutip,thmip)
    time.sleep(3)
    
    filetransfer_script("transfer_linein_host","C:\\lineInOri.wav","//lineInOri.wav","thm",host_ip_add,thmip)
    time.sleep(3)
    filetransfer_script("transfer_micin_host","C:\\micInOri.wav","//micInOri.wav","thm",host_ip_add,thmip)
    if autoduration:
        with contextlib.closing(wave.open(song,'r')) as f:
            framesize = f.getnframes()
            framerate = f.getframerate()
            duration = framesize/float(framerate)
            #duration = int(duration)
            logging(hdalog,song + " duration is " + str(duration)) 
            print song + " duration is " + str(duration)

    
    if source == "Mic":
        source = "Rear\ Mic"
    print "Input Source = " + source
    temp = worker1.execute("amixer -c 0 sset 'Input Source' " + source)
    if temp == '':
       print 'Input Souce was in wrong format,for front mic and rear mic please adhere to following input format: "Rear\ Mic" and "Front\ Mic"'
       logging(hdalog,'Input Souce was in wrong format,for front mic and rear mic please adhere to following input format: "Rear\ Mic" and "Front\ Mic"')
       sys.exit(1)
    else:
       print "input source message: " + temp
       logging(hdalog,"input source message: " + temp)
    
    # DEBUG
    #print "The current SUT is " + worker1.execute("ifconfig | grep " + sutip)
    
    worker1.login(sutip, 2300)
    
    worker1.execute("amixer set -c 0 PCM 70% unmute")
    worker1.execute("amixer set -c 0 Master 70% unmute")
    worker1.execute("amixer set -c 0 'Front Mic' 70% unmute")
    worker1.execute("amixer set -c 0 'Rear Mic' 70% unmute")
    worker1.execute("amixer set -c 0 'Front Mic Boost' 70% unmute")
    worker1.execute("amixer set -c 0 'Rear Mic Boost' 70% unmute")
    #worker1.execute("amixer set -c 0 Capture Capture 80% unmute")
    worker1.execute("amixer set -c 0 Line 70% unmute")
    worker1.execute("amixer set -c 0 Headphone 70% unmute")
 
    if mute == False:
       if channel == False:
            temp = worker1.execute("amixer set -c 0 PCM " + master + " unmute")
            if temp != '' and master in temp:
                print temp
                logging(hdalog,temp) 
            else:
                print 'Value of PCM volume is not tally with specified value'
                print temp
                logging(hdalog,temp) 
            temp = worker1.execute("amixer set -c 0 Master " + master + " unmute")
            if temp != '' and master in temp:
                print temp 
                logging(hdalog,temp)  
            else:
                print 'Value of Master volume is not tally with specified value'
                print temp
                logging(hdalog,temp) 
            temp = worker1.execute("amixer set -c 0 Capture Capture " + capture + " unmute")
            if temp != '' and capture in temp:
                print temp 
                logging(hdalog,temp) 
            else:
                print 'Value of Capture volume is not tally with specified value'
                print temp
                logging(hdalog,temp) 

       else:
            temp = worker1.execute("amixer set -c 0 PCM " + leftchnl + "," + rightchnl + " unmute")
            if temp != '' and leftchnl in temp and rightchnl in temp:
                print temp 
                logging(hdalog,temp) 
            else:
                print 'Value of Left/Right PCM volume is not tally with specified value'
                print temp
                logging(hdalog,temp) 
            temp = worker1.execute("amixer set -c 0 Master " +  master + " unmute")
            if temp != '' and master in temp:
                print temp 
                logging(hdalog,temp) 
            else:
                print 'Value of Master volume is not tally with specified value'
                print temp
                logging(hdalog,temp) 
            worker1.execute("amixer set -c 0 Capture Capture " + leftchnl + "," + rightchnl + " unmute")
            if temp != '' and leftchnl in temp and rightchnl in temp:
                print temp 
                logging(hdalog,temp) 
            else:
                print 'Value of Left/Right capture volume is not tally with specified value'
                print temp
                logging(hdalog,temp) 
    elif mute == True:
       temp = worker1.execute("amixer set -c 0 PCM mute")
       if temp != '' and "off" in temp:
           print temp 
           logging(hdalog,temp) 
       else:
           print 'PCM volume is not muted'
           print temp
           logging(hdalog,temp) 
       temp = worker1.execute("amixer set -c 0 Master mute")
       if temp != '' and "off" in temp:
           print temp 
           logging(hdalog,temp) 
       else:
           print 'Master volume is not muted'
           print temp
           logging(hdalog,temp) 


    worker1.execute("rm -rf " + output)
    
    # DEBUG
    #print "The current SUT is " + worker1.execute("ifconfig | grep " + sutip)
    
    worker1.login(sutip, 2300)
    
    if not mp3:
        #p1 = Thread(target=playing,args=[duration,song])
        #p1.daemon = True
        #p1.start()
        worker1.timeexecute("aplay -D hw:0,0 /" + song)
    else:
        worker1.timeexecute("gst-launch playbin2 uri=file://" + song)    
        
    if autoduration:
        #os.system("arecord -d " + str(duration) + " -f cd " + output)
        worker1.execute("arecord -D hw:0,0 -d " + str(duration) + " -f cd " + output)
    else:
        p1 = Thread(target=time_elapse,args=[rec_duration,song + " recording"])
        p1.daemon = True
        p1.start()
        worker1.execute("arecord -d " + rec_duration + " -f cd " + output)
    

    #if os.path.exists(output):
    if worker1.timefiletrace(output):
        print "\n" + output + " file exists"
        logging(hdalog,"\n" + output + " file exists")

## THIS PART STILL RUNS ON SUT MODE

        filetransfer_script("transfer_linein_host","C:\\lineInOri.wav","//lineInOri.wav","thm",host_ip_add,thmip)
        time.sleep(3)
        filetransfer_script("transfer_micin_host","C:\\micInOri.wav","//micInOri.wav","thm",host_ip_add,thmip)
        with contextlib.closing(wave.open(output,'r')) as f:
            outframesize = f.getnframes()
            outframerate = f.getframerate()
            outduration = outframesize/float(outframerate)
            logging(hdalog,output + " duration is " + str(outduration)) 
            print output + " duration is " + str(outduration)
        
        
 
        
        time.sleep(5)
        outputname = "C:\output\output_" + get_date() + "_" + get_current_time() + ".wav"
        print "Output file name : " + outputname
        
        filetransfer_script_linux("transfer_output", "/" + output, outputname, "sut", thmip, sutip) # Send test audio recording to autoear machine
        #filetransfer_script_linux(script_name,ori_loc,target_loc,obj,dest_ip,source_ip)
        
        autoear = GenericCommand()
        autoear.login(thmip)
        #autoear.execute("DEL C:\output.wav")
        filetrace = autoear.timefiletrace(outputname)
        print filetrace        
        logging(hdalog,filetrace) 
    else:
        print "\n" + output + " file not found"
        logging(hdalog,"\n" + output + " file not found") 
        sys.exit(1)
 
    try:
       print "gold file = " + gold
       autoear.execute("mkdir C:\\AudioCompare_Log")
       default_threshold = 90
       autoear.timeexecute("C:\WinAutoEar\AudioCompare.exe compare " + str(default_threshold) + " " + gold + " " + outputname + " C:\AudioCompare_Log\compare.log")
       counter = 0
       while counter <= timeout:
           if counter >= timeout - 1:
                task = "AudioCompare.exe"
                checker = autoear.execute("tasklist")
                logging(hdalog,checker) 
                if "AudioCompare.exe" in checker:
                    autoear.execute("taskkill /F /im " + task)
                    print "AudioCompare terminated"
                    logging(hdalog,"AudioCompare terminated")
                    break
                else:
                    pass
           time.sleep(1)
           counter = counter + 1
       
    except Exception, error:
       type_, value_, traceback_ = sys.exc_info()
       print str(error)
       logging(hdalog,str(error))
       print traceback.format_tb(traceback_)
       logging(hdalog,traceback.format_tb(traceback_))
       print "exception caught"
       sys.exit(1)


    output = autoear.execute("type C:\\AudioCompare_Log\\compare.log")
    output_list = output.split("\n")
    for line in output_list:
        print line 
    verdict = result_parser(output_list,default_threshold)
    """
    masterint = master.split("%")[0]
    captureint = capture.split("%")[0]
    if int(masterint) <= 0 or int(captureint) <= 0:
        mute = True
    """
    print "Mute: " + str(mute)
    #Retrieve comparable length between two clips
    for i in output_list:
        if "compared" in i:
             length = i.split(" ")[-1]
             length = length[:-1]
    print "Comparable length : " + str(length) + " seconds"
    if len(length) > 1:
        length = float(length)
    else:
        length = int(length)

    if verdict and int(length) > 5:
        print "Master volume: " + master
        print "Capture volume: " + capture
        logging(hdalog,"Master volume: " + master)
        logging(hdalog,"Capture volume: " + capture)
        print "FINAL VERDICT: PASS"
        logging(hdalog,"FINAL VERDICT: PASS")
        autoear.execute("DEL C:\output\*.wav*.fft")
        autoear.execute("DEL C:\*.wav*.fft")
        autoear.execute("RENAME C:\\AudioCompare_Log\\compare.log compare_" + get_date() + "_" + get_current_time() + "_volume_" + master + "_capture_" + capture + "_PASS_" + ".log") 
        sys.exit(0)
    elif "Could not find audio content on clip 2, channel 0" in output and "Could not find audio content on clip 2, channel 1" in output and mute == True:
        print "Master volume: " + master
        print "Capture volume: " + capture
        logging(hdalog,"Master volume: " + master)
        logging(hdalog,"Capture volume: " + capture)
        print "Clip 2 detected silent while mute = True"
        logging(hdalog,"Clip 2 detected silent while mute = True")
        print "FINAL VERDICT: PASS"
        logging(hdalog,"FINAL VERDICT: PASS")
        autoear.execute("DEL C:\output\*.wav*.fft")
        autoear.execute("DEL C:\*.wav*.fft")
        autoear.execute("RENAME C:\\AudioCompare_Log\\compare.log compare_" + get_date() + "_" + get_current_time() + "_volume_" + master + "_capture_" + capture + "_Muted_" + "_PASS_" + ".log") 
        sys.exit(0)
    elif int(length) < 5 and mute == True:
        print "Master volume: " + master
        print "Capture volume: " + capture
        logging(hdalog,"Master volume: " + master)
        logging(hdalog,"Capture volume: " + capture)
        print "Comparable length is less than 5 seconds while mute = True"
        logging(hdalog,"Comparable length is less than 5 seconds while mute = True")
        print "FINAL VERDICT: PASS"
        logging(hdalog,"FINAL VERDICT: PASS")
        autoear.execute("DEL C:\output\*.wav*.fft")
        autoear.execute("DEL C:\*.wav*.fft")
        autoear.execute("RENAME C:\\AudioCompare_Log\\compare.log compare_" + get_date() + "_" + get_current_time() + "_volume_" + master + "_capture_" + capture + "_Muted_" + "_PASS_" + ".log")
        sys.exit(0)
    else:
        print "Master volume: " + master
        print "Capture volume: " + capture
        logging(hdalog,"Master volume: " + master)
        logging(hdalog,"Capture volume: " + capture)
        if int(length) < 5:
              print "Comparable length is less than 5 seconds while mute = False"
              logging(hdalog,"Comparable length is less than 5 seconds while mute = False")
        print "FINAL VERDICT: FAIL"        
        logging(hdalog,"FINAL VERDICT: FAIL")
        autoear.execute("DEL C:\output\*.wav*.fft")
        autoear.execute("DEL C:\*.wav*.fft")
        autoear.execute("RENAME C:\\AudioCompare_Log\\compare.log compare_" + get_date() + "_" + get_current_time() + "_volume_" + master + "_capture_" + capture + "_FAIL_" + ".log") 
        sys.exit(1)
     
 
    
    


